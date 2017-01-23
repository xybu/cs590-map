#!/usr/bin/env python3

import argparse
from collections import namedtuple
import pprint

import constants
import metis
import models
import utils_input


MetisInput = namedtuple('MetisInput', ('pms', 'pms_unused', 'sw_cpu_shares', 'vhost_cpu_shares',
                                       'sw_imbalance_factor', 'vhost_imbalance_factor'))

ResultRank = namedtuple('ResultRank', ('tier', 'pms_over', 'pms_under', 'pms_used', 'pms_over_degree', 'min_cut'))

GraphProperties = namedtuple('GraphProperties', ('total_edge_weight', 'total_vertex_weight', 'total_vhost_weight',
                                                 'num_edges', 'num_vertices'))

PartitionResult = namedtuple('PartitionResult', ('min_cut', 'assignment',
                                                 'pms_used', 'pms_unused', 'pms_over', 'pms_under',
                                                 'switch_cap_usages', 'switch_cpu_usages', 'vhost_cpu_usages',
                                                 'total_cpu_usages', 'switch_share_weights', 'vhost_share_weights'))


def call_metis(graph, params):
    """
    :param networkx.Graph graph:
    :param MetisInput params:
    :return:
    """
    print('sw_cpu_shares:   ' + str(params.sw_cpu_shares))
    print('vh_cpu_shares:   ' + str(params.vhost_cpu_shares))
    num_pms = len(params.pms)
    if num_pms == 1:
        min_cut = 0
        assignment = [params.pms[0].pm_id] * graph.number_of_nodes()
    else:
        switch_cap_shares = [pm.capacity_func.eval(params.sw_cpu_shares[i]) for i, pm in enumerate(params.pms)]
        norm_switch_cap_shares = normalize_shares(switch_cap_shares)
        norm_vhost_cpu_shares = normalize_shares(params.vhost_cpu_shares)
        imbalance_vec = (1 + params.sw_imbalance_factor, 1 + params.vhost_imbalance_factor)
        print('sw_cap_shares:   [' + ', '.join(['%.3f' % v for v in switch_cap_shares]) + ']')
        print('imbalance_vec:   (sw=%.2f, vhost=%.2f)' % imbalance_vec)
        min_cut, assignment = metis.part_graph(graph, nparts=num_pms,
                                               tpwgts=list(zip(norm_switch_cap_shares, norm_vhost_cpu_shares)),
                                               ubvec=imbalance_vec, recursive=False)
        # Translate array index to PM #.
        pm_index_mapping = [pm.pm_id for pm in params.pms]
        for i, a in enumerate(assignment):
            assignment[i] = pm_index_mapping[a]
    return min_cut, assignment


def normalize_shares(shares):
    shares = [v if v > 0 else 1 for v in shares]
    total = sum(shares)
    norm_shares = [v / total for v in shares]
    if sum(norm_shares) != 1:
        # Add the division error to the max goal set.
        norm_shares[norm_shares.index(max(norm_shares))] += 1 - sum(norm_shares)
    return norm_shares


def dump_args(args):
    print('Command-line arguments:')
    for k, v in args.__dict__.items():
        print('  %s: %s' % (k, v))
    print()


def dump_parameters():
    print('Program parameters:')
    for k in constants.__all__:
        print('  %s: %s' % (k, getattr(constants, k)))
    print()


def read_graph(graph_filepath, vhost_filepath):
    # Read graph input and vhost CPU file, and then update the graph properties.
    graph = utils_input.parse_chaco_input(graph_filepath)
    vhost_requirements = utils_input.read_int_file(vhost_filepath)
    utils_input.nxgraph_add_node_property(graph, constants.NODE_CPU_WEIGHT_KEY, vhost_requirements)
    total_vertex_weight = utils_input.nxgraph_node_property_sum(graph, constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY)
    total_edge_weight = utils_input.nxgraph_edge_property_sum(graph, constants.EDGE_WEIGHT_KEY)
    graph_properties = GraphProperties(total_edge_weight=total_edge_weight,
                                       total_vertex_weight=total_vertex_weight,
                                       total_vhost_weight=sum(vhost_requirements),
                                       num_edges=graph.number_of_edges(),
                                       num_vertices=graph.number_of_nodes())
    graph.graph['node_weight_attr'] = (constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, constants.NODE_CPU_WEIGHT_KEY)
    print('Graph stats:')
    print('  Number of vertices:     %d' % graph_properties.num_vertices)
    print('  Number of edges:        %d' % graph_properties.num_edges)
    print('  Total edge weight:      %d' % graph_properties.total_edge_weight)
    print('  Total vertex weight:    %d' % graph_properties.total_vertex_weight)
    print('  Total vhost CPU weight: %d' % graph_properties.total_vhost_weight)
    print()
    return graph, graph_properties


def read_pm_file(filepath):
    machines = models.Machine.read_machines_from_file(filepath)
    total_machines = len(machines)
    print('Read %d PMs from input:' % total_machines)
    for p in machines:
        print('  ' + str(p))
    print()
    return machines, total_machines


def get_initial_input(pms, sw_imbalance_factor, vhost_imbalance_factor):
    """
    :param [models.Machine] pms:
    :param float sw_imbalance_factor:
    :param float vhost_imbalance_factor:
    :return MetisInput:
    """
    sw_cpu_shares = []
    vhost_cpu_shares = []
    for pm in pms:
        sw_cpu_share = max(constants.INIT_SWITCH_CPU_SHARES, pm.min_switch_cpu_share)
        sw_cpu_shares.append(sw_cpu_share)
        vhost_cpu_shares.append(pm.max_cpu_share - sw_cpu_share)
    return MetisInput(pms=tuple(pms), pms_unused=(),
                      sw_cpu_shares=tuple(sw_cpu_shares), vhost_cpu_shares=tuple(vhost_cpu_shares),
                      sw_imbalance_factor=sw_imbalance_factor, vhost_imbalance_factor=vhost_imbalance_factor)


def calc_subset_weight_sum(graph, pms, key, assignment):
    """
    :param networkx.Graph graph:
    :param [models.Machine] pms:
    :param str key:
    :param [int] assignment:
    :return dict[int, int | float]: A dict whose key is PM # and value is the sum of
        the weights of nodes assigned to it.
    """
    set_weights = {pm.pm_id: 0 for pm in pms}
    for i, pm_id in enumerate(assignment):
        set_weights[pm_id] += graph.node[i + 1][key]
    return set_weights


# def calc_subsets(pms, assignment):
#     subsets = {pm.pm_id: [] for pm in pms}
#     for i, pm_id in enumerate(assignment):
#         subsets[pm_id].append(i + 1)
#     return subsets


def is_pm_overutilized(pm, total_cpu_usage, delta=0):
    return total_cpu_usage + delta > int(pm.max_cpu_share * constants.PM_OVER_UTILIZED_THRESHOLD)


def is_pm_underutilized(pm, total_cpu_usage, delta=0):
    return int(pm.max_cpu_share * constants.PM_UNDER_UTILIZED_THRESHOLD) > total_cpu_usage + delta


def pm_overutilized_shares(pm, total_usage, delta=0):
    return total_usage + delta - pm.max_cpu_share


def pm_underutilized_shares(pm, total_usage, delta=0):
    return int(pm.max_cpu_share * constants.PM_UNDER_UTILIZED_THRESHOLD) - total_usage - delta


def analyze_result(graph, graph_properties, input, min_cut, assignment):
    """
    :param networkx.Graph graph:
    :param GraphProperties graph_properties:
    :param MetisInput input:
    :param int min_cut:
    :param [int] assignment:
    :return:
    """
    pms_unused = dict()
    pms_used = dict()
    pms_over = dict()
    pms_under = dict()
    switch_share_weights = dict()
    vhost_share_weights = dict()
    switch_cpu_usages = dict()
    total_cpu_usages = dict()
    switch_cap_usages = calc_subset_weight_sum(graph, input.pms, constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, assignment)
    vhost_cpu_usages = calc_subset_weight_sum(graph, input.pms, constants.NODE_CPU_WEIGHT_KEY, assignment)
    assert(min_cut <= graph_properties.total_edge_weight)
    assert(len(assignment) == graph_properties.num_vertices)
    assert(sum(switch_cap_usages.values()) == graph_properties.total_vertex_weight)
    assert(sum(vhost_cpu_usages.values()) == graph_properties.total_vhost_weight)
    pms_ok_count = 0
    for pm in input.pms:
        if pm.pm_id not in assignment:
            pms_unused[pm.pm_id] = pm
            switch_cpu_usages[pm.pm_id] = 0
            total_cpu_usages[pm.pm_id] = 0
        else:
            pms_used[pm.pm_id] = pm
            switch_cpu_usages[pm.pm_id] = pm.capacity_func.reverse_eval(switch_cap_usages[pm.pm_id])
            total_cpu_usage = switch_cpu_usages[pm.pm_id] + vhost_cpu_usages[pm.pm_id]
            total_cpu_usages[pm.pm_id] = total_cpu_usage
            if is_pm_overutilized(pm, total_cpu_usage):
                pms_over[pm.pm_id] = pm_overutilized_shares(pm, total_cpu_usage)
            elif is_pm_underutilized(pm, total_cpu_usage):
                pms_under[pm.pm_id] = pm_underutilized_shares(pm, total_cpu_usage)
            else:
                pms_ok_count += 1
        vhost_share_weights[pm.pm_id] = vhost_cpu_usages[pm.pm_id] / graph_properties.total_vhost_weight
        switch_share_weights[pm.pm_id] = switch_cap_usages[pm.pm_id] / graph_properties.total_vertex_weight
    assert(len(pms_unused) + len(pms_used) == len(input.pms))
    assert(len(pms_over) + len(pms_under) + pms_ok_count == len(pms_used))
    return PartitionResult(min_cut=min_cut, assignment=assignment,
                           pms_used=pms_used, pms_unused=pms_unused, pms_over=pms_over, pms_under=pms_under,
                           switch_cap_usages=switch_cap_usages, switch_cpu_usages=switch_cpu_usages,
                           vhost_cpu_usages=vhost_cpu_usages, total_cpu_usages=total_cpu_usages,
                           switch_share_weights=switch_share_weights, vhost_share_weights=vhost_share_weights)


def rank_result(result):
    """
    :param PartitionResult result:
    :return:
    """
    pms_over_num = len(result.pms_over)
    if pms_over_num > 0:
        tier = 1
        pms_over_degree = 0
        for pm_id, over_shares in result.pms_over.items():
            deg = int(over_shares * 1000 / result.pms_used[pm_id].max_cpu_share)
            if deg > pms_over_degree:
                pms_over_degree = deg
    else:
        tier = 0
        pms_over_degree = 0
    return ResultRank(tier=tier, pms_over=pms_over_num, pms_under=len(result.pms_under), pms_used=len(result.pms_used),
                      pms_over_degree=pms_over_degree, min_cut=result.min_cut)


def brute_force_imbalance_vector(graph, graph_properties, pms):
    """
    :param networkx.Graph graph:
    :param GraphProperties graph_properties:
    :param [models.Machine] pms:
    :return:
    """
    base = get_initial_input(pms, constants.DEFAULT_SW_IMBALANCE_FACTOR, constants.DEFAULT_VHOST_IMBALANCE_FACTOR)
    for i in range(0, 51):
        for j in range(0, 51):
            metis_input = base._replace(sw_imbalance_factor=i / 100, vhost_imbalance_factor=j / 100)
            min_cut, assignment = call_metis(graph, metis_input)
            result = analyze_result(graph, graph_properties, metis_input, min_cut, assignment)
            rank = rank_result(result)
            print('%s:\n%s\n%s\n\n' % (metis_input, result, rank))


def main():
    parser = argparse.ArgumentParser(description='A refined graph partition algorithm based on METIS.')
    parser.add_argument('-g', '--graph-file', type=str, required=True, help='File to read input graph from.')
    parser.add_argument('-p', '--pm-file', type=str, required=True, help='File to read PM information.')
    parser.add_argument('-c', '--vhost-cpu-file', type=str, required=True, help='File to read vhost CPU information.')
    parser.add_argument('-o', '--out', type=str, required=False, default=None,
                        help='If given, will generate output files to this dir.')
    parser.add_argument('--sw-imbalance-factor', type=float, default=constants.DEFAULT_SW_IMBALANCE_FACTOR,
                        help='Imbalance factor for switch constraint. Use a value in [0, 0.15].')
    parser.add_argument('--vhost-imbalance-factor', type=float, default=constants.DEFAULT_VHOST_IMBALANCE_FACTOR,
                        help='Imbalance factor for vhost CPU constraint. Use a value in [0, 0.15].')
    parser.add_argument('--find-imbalance-vec', default=False,
                        action='store_true', help='If set, brute force potentially best imbalance vector.')
    args = parser.parse_args()

    dump_args(args)
    dump_parameters()

    machines, total_machines = read_pm_file(args.pm_file)
    graph, graph_properties = read_graph(args.graph_file, args.vhost_cpu_file)

    if args.find_imbalance_vec:
        brute_force_imbalance_vector(graph, graph_properties, machines)


if __name__ == '__main__':
    main()

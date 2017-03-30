#!/usr/bin/env python3

import argparse
from collections import namedtuple
import concurrent.futures
import csv
import enum
import functools
import math
import os
import sys
import queue

import click
import tabulate
import matplotlib.pyplot as plt
import networkx as nx

import constants
import metis
import models
import utils_input


MetisInput = namedtuple('MetisInput', ('pms', 'pms_unused', 'sw_cpu_shares', 'vhost_cpu_shares', 'seed',
                                       'sw_imbalance_factor', 'vhost_imbalance_factor'))

ResultRank_Fields = ('tier', 'pms_over', 'pms_under', 'pms_unused', 'pms_used', 'pms_over_degree', 'min_cut')
ResultRank = namedtuple('ResultRank', ResultRank_Fields)

GraphProperties = namedtuple('GraphProperties', ('total_edge_weight', 'total_vertex_weight', 'total_vhost_weight',
                                                 'num_edges', 'num_vertices'))

PartitionResult = namedtuple('PartitionResult', ('min_cut', 'assignment',
                                                 'pms_used', 'pms_unused', 'pms_over', 'pms_under',
                                                 'switch_cap_usages', 'switch_cpu_usages', 'vhost_cpu_usages',
                                                 'total_cpu_usages', 'share_weights'))


class DominanceLevel(enum.Enum):
    NO_DOMINANCE = 0
    MIN_CUT_EXISTS = 1
    SUB_LEVEL_DOMINANCE = 2
    TIER_LEVEL_DOMINANCE = 3


class ResultHistory:

    MAX_TIER = 1

    def __init__(self):
        self.by_tiers = {i: dict() for i in range(0, self.MAX_TIER + 1)}

    def is_rank_dominated_when_no_over_pm(self, rank):
        """
        For a rank without over-utilized PMs, there is no issue with fidelity. We rank by first smallest number of
        PMs used, then smallest min cut.
        :param ResultRank rank:
        :return True | False:
        """
        by_used = self.by_tiers[0]
        if len(by_used) == 0:
            return DominanceLevel.NO_DOMINANCE

        min_pms_used = min(by_used.keys())
        if min_pms_used < rank.pms_used:
            return DominanceLevel.SUB_LEVEL_DOMINANCE
        elif min_pms_used > rank.pms_used:
            return DominanceLevel.NO_DOMINANCE

        by_min_cut = by_used[rank.pms_used]
        min_min_cut = min(by_min_cut.keys())
        if min_min_cut < rank.min_cut:
            return DominanceLevel.SUB_LEVEL_DOMINANCE
        elif min_min_cut == rank.min_cut:
            return DominanceLevel.MIN_CUT_EXISTS

        return DominanceLevel.NO_DOMINANCE

    def save_result_when_no_over_pm(self, input, result, rank):
        by_pms_used = self.by_tiers[rank.tier]
        # Could use defaultdict. But anyway.
        if rank.pms_used not in by_pms_used:
            by_pms_used[rank.pms_used] = dict()
        by_min_cut = by_pms_used[rank.pms_used]
        if rank.min_cut not in by_min_cut:
            by_min_cut[rank.min_cut] = []
        by_min_cut[rank.min_cut].append((input, result, rank))

    def best_candidates_when_no_over_pm(self):
        by_pms_used = self.by_tiers[0]
        if len(by_pms_used) > 0:
            by_min_cut = by_pms_used[min(by_pms_used.keys())]
            if len(by_min_cut) > 0:
                return tuple(by_min_cut[min(by_min_cut.keys())])
        return None

    def traverse_results_when_no_over_pm(self, f):
        by_pms_used = self.by_tiers[0]
        for pms_used_key in sorted(by_pms_used.keys()):
            by_min_cut = by_pms_used[pms_used_key]
            for min_cut_key in sorted(by_min_cut.keys()):
                for item in by_min_cut[min_cut_key]:
                    f(*item)

    def is_rank_dominated_with_over_pm(self, rank):
        """
        For a rank with any over-utilized PM, fidelity becomes a concern. We rank first by smallest degree to which
        the most over-utilized PM is over-utilized, then smallest number of over-utilized PMs, then min cut.
        :param ResultRank rank:
        :return True | False:
        """
        by_over_degree = self.by_tiers[1]
        if len(by_over_degree) == 0:
            return DominanceLevel.NO_DOMINANCE

        min_over_degree = min(by_over_degree.keys())
        if min_over_degree < rank.pms_over_degree:
            return DominanceLevel.SUB_LEVEL_DOMINANCE
        elif min_over_degree > rank.pms_over_degree:
            return DominanceLevel.NO_DOMINANCE

        by_pms_over = by_over_degree[rank.pms_over_degree]
        min_pms_over = min(by_pms_over.keys())
        if min_pms_over < rank.pms_over:
            return DominanceLevel.SUB_LEVEL_DOMINANCE
        elif min_pms_over > rank.pms_over:
            return DominanceLevel.NO_DOMINANCE

        by_min_cut = by_pms_over[rank.pms_over]
        min_min_cut = min(by_min_cut.keys())
        if min_min_cut < rank.min_cut:
            return DominanceLevel.SUB_LEVEL_DOMINANCE
        elif min_min_cut == rank.min_cut:
            return DominanceLevel.MIN_CUT_EXISTS

        return DominanceLevel.NO_DOMINANCE

    def save_result_with_over_pm(self, input, result, rank):
        by_over_degree = self.by_tiers[rank.tier]
        if rank.pms_over_degree not in by_over_degree:
            by_over_degree[rank.pms_over_degree] = dict()
        by_pms_over = by_over_degree[rank.pms_over_degree]
        if rank.pms_over not in by_pms_over:
            by_pms_over[rank.pms_over] = dict()
        by_min_cut = by_pms_over[rank.pms_over]
        if rank.min_cut not in by_min_cut:
            by_min_cut[rank.min_cut] = []
        by_min_cut[rank.min_cut].append((input, result, rank))

    def best_candidates_with_over_pm(self):
        by_over_degree = self.by_tiers[1]
        if len(by_over_degree) > 0:
            by_pms_over = by_over_degree[min(by_over_degree.keys())]
            if len(by_pms_over) > 0:
                by_min_cut = by_pms_over[min(by_pms_over.keys())]
                if len(by_min_cut) > 0:
                    return tuple(by_min_cut[min(by_min_cut.keys())])
        return None

    def traverse_results_with_over_pm(self, f):
        by_over_degree = self.by_tiers[1]
        for over_degree_key in sorted(by_over_degree.keys()):
            by_pms_over = by_over_degree[over_degree_key]
            for pms_over_key in sorted(by_pms_over.keys()):
                by_min_cut = by_pms_over[pms_over_key]
                for min_cut_key in sorted(by_min_cut.keys()):
                    for item in by_min_cut[min_cut_key]:
                        f(*item)

    def is_rank_dominated(self, rank):
        """
        :param ResultRank rank:
        :return DominanceLevel:
        """
        for i in range(0, rank.tier):
            if len(self.by_tiers[i]) > 0:
                return DominanceLevel.TIER_LEVEL_DOMINANCE
        if rank.tier == 0:
            return self.is_rank_dominated_when_no_over_pm(rank)
        elif rank.tier == 1:
            return self.is_rank_dominated_with_over_pm(rank)
        raise ValueError('Unknown tier value "%d" in rank %s.' % (rank.tier, rank))

    def best_candidates(self):
        if len(self.by_tiers[0]) > 0:
            return self.best_candidates_when_no_over_pm()
        elif len(self.by_tiers[1]) > 0:
            return self.best_candidates_with_over_pm()
        return ()

    def save_result(self, input, result, rank):
        """
        :param MetisInput input:
        :param PartitionResult result:
        :param ResultRank rank:
        """
        if rank.tier == 0:
            self.save_result_when_no_over_pm(input, result, rank)
        elif rank.tier == 1:
            self.save_result_with_over_pm(input, result, rank)
        else:
            raise ValueError('Unknown tier value "%d" (%s) in rank %s.' % (
                rank.tier, type(rank.tier).__name__, rank))

    def traverse(self, f):
        self.traverse_results_when_no_over_pm(f)
        self.traverse_results_with_over_pm(f)


class SerialResultHistory:
    """ A store that saves results linearly. """

    def __init__(self):
        self.hist = []

    def save_result(self, input, result, rank):
        self.hist.append((input, result, rank))

    def traverse(self, f):
        for i in self.hist:
            f(*i)


class ResultHash:

    def __init__(self):
        self.pms_used_history = set()
        self.assignment_history = set()

    def register_pm_used_input(self, pms):
        pm_ids = tuple(sorted([pm.pm_id for pm in pms]))
        self.pms_used_history.add(pm_ids)

    def is_pms_used_input_registered(self, pms):
        pm_ids = tuple(sorted([pm.pm_id for pm in pms]))
        return pm_ids in self.pms_used_history

    def register_assignment(self, assignment):
        self.assignment_history.add(assignment)

    def is_assignment_known(self, assignment):
        return assignment in self.assignment_history


def visualize_assignment(graph, assignment, outfile_path=None, show=False):
    try:
        edge_weights = [math.log(w) / 2.4 for (u, v, w) in graph.edges(data='weight')]
    except:
        edge_weights = 1

    try:
        weights = [n[1][constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY] for n in graph.nodes(data=True)]
        sizes = [math.pow(w, 0.55) * 6 for w in weights]
    except KeyError:
        weights = 50
        sizes = weights

    fig = plt.figure()
    # plt.title("Visualization of \"%s\"" % args.path, {'fontweight': 'bold'})
    plt.axis('off')
    pos = nx.nx_agraph.graphviz_layout(graph)

    nx.draw_networkx_nodes(graph, pos, node_size=sizes, node_color=assignment, cmap=plt.get_cmap('plasma'), alpha=0.95)
    nx.draw_networkx_edges(graph, pos, width=edge_weights, alpha=0.7)

    # nx.draw(graph, pos, with_labels=False, node_color=degrees, node_size=weights, cmap=plt.get_cmap('viridis'))
    fig.tight_layout()
    if outfile_path is not None:
        for fmt in ('svg', 'pdf'):
            plt.savefig(outfile_path + '.' + fmt, transparent=True, bbox_inches='tight', format=fmt, pad_inches=-0.4)
    if show:
        plt.show()
    plt.close()


def call_metis(graph, params, **metis_options):
    """
    :param networkx.Graph graph:
    :param MetisInput params:
    :return:
    """
    # print('sw_cpu_shares:   ' + str(params.sw_cpu_shares))
    # print('vh_cpu_shares:   ' + str(params.vhost_cpu_shares))
    num_pms = len(params.pms)
    if num_pms == 1:
        min_cut = 0
        assignment = [params.pms[0].pm_id] * graph.number_of_nodes()
    else:
        switch_cap_shares = [pm.capacity_func.eval(params.sw_cpu_shares[i]) for i, pm in enumerate(params.pms)]
        norm_switch_cap_shares = normalize_shares(switch_cap_shares)
        norm_vhost_cpu_shares = normalize_shares(params.vhost_cpu_shares)
        imbalance_vec = (1 + params.sw_imbalance_factor, 1 + params.vhost_imbalance_factor)
        # print('sw_cap_shares:   [' + ', '.join(['%.3f' % v for v in switch_cap_shares]) + ']')
        # print('imbalance_vec:   (sw=%.2f, vhost=%.2f)' % imbalance_vec)
        min_cut, assignment = metis.part_graph(graph, nparts=num_pms,
                                               tpwgts=list(zip(norm_switch_cap_shares, norm_vhost_cpu_shares)),
                                               ubvec=imbalance_vec, recursive=False,
                                               seed=params.seed)
        # Translate array index to PM #.
        pm_index_mapping = [pm.pm_id for pm in params.pms]
        for i, a in enumerate(assignment):
            assignment[i] = pm_index_mapping[a]
    return min_cut, tuple(assignment)


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
    for k, v in sorted(args.__dict__.items()):
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
    graph.graph['edge_weight_attr'] = constants.EDGE_WEIGHT_KEY
    graph.graph['node_weight_attr'] = (constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, constants.NODE_CPU_WEIGHT_KEY)
    return graph, graph_properties


def print_graph_properties(graph_properties):
    print('Graph stats:')
    print('  Number of vertices:     %d' % graph_properties.num_vertices)
    print('  Number of edges:        %d' % graph_properties.num_edges)
    print('  Total edge weight:      %d' % graph_properties.total_edge_weight)
    print('  Total vertex weight:    %d' % graph_properties.total_vertex_weight)
    print('  Total vhost CPU weight: %d' % graph_properties.total_vhost_weight)
    print()


def read_pm_file(filepath):
    machines = models.Machine.read_machines_from_file(filepath)
    return machines


def dump_pms(machines):
    print('Read %d PMs from input:' % len(machines))
    for p in machines:
        print('  ' + p.full_str)
    print()


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
    """ How many shares beyond max limit. """
    return total_usage + delta - pm.max_cpu_share


def pm_underutilized_shares(pm, total_usage, delta=0):
    """ How many more shares needed to reach in-range level. """
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
    switch_cpu_usages = dict()
    total_cpu_usages = dict()
    switch_cap_usages = calc_subset_weight_sum(graph, input.pms, constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, assignment)
    vhost_cpu_usages = calc_subset_weight_sum(graph, input.pms, constants.NODE_CPU_WEIGHT_KEY, assignment)
    share_weights = dict()
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
                assert(pms_over[pm.pm_id] >= int(pm.max_cpu_share * (constants.PM_OVER_UTILIZED_THRESHOLD - 1)))
            elif is_pm_underutilized(pm, total_cpu_usage):
                pms_under[pm.pm_id] = pm_underutilized_shares(pm, total_cpu_usage)
                assert(pms_under[pm.pm_id] > 0)
            else:
                pms_ok_count += 1
        weight = round(switch_cap_usages[pm.pm_id] / graph_properties.total_vertex_weight +
                       vhost_cpu_usages[pm.pm_id] / graph_properties.total_vhost_weight, 6)
        share_weights[pm.pm_id] = weight
    assert(len(pms_unused) + len(pms_used) == len(input.pms))
    assert(len(pms_over) + len(pms_under) + pms_ok_count == len(pms_used))
    return PartitionResult(min_cut=min_cut, assignment=assignment,
                           pms_used=pms_used, pms_unused=pms_unused, pms_over=pms_over, pms_under=pms_under,
                           switch_cap_usages=switch_cap_usages, switch_cpu_usages=switch_cpu_usages,
                           vhost_cpu_usages=vhost_cpu_usages, total_cpu_usages=total_cpu_usages,
                           share_weights=share_weights)


def print_result_brief(result, indent=0):
    """
    :param PartitionResult result:
    :param int indent:
    :return:
    """
    indent = ' ' * indent
    click.echo('%s<PartitionResult> min_cut=%d' % (indent, result.min_cut))
    for weight, pm_id in sorted([(w, pm_id) for pm_id, w in result.share_weights.items()], reverse=True):
        w_str = '[%6.3f%%]' % (weight * 50)
        try:
            pm = result.pms_used[pm_id]
        except KeyError:
            pm = result.pms_unused[pm_id]
        stat_str = 'sw_cap=%d, sw_cpu=%d, vhost_cpu=%d, total_cpu=%d' % (
            result.switch_cap_usages[pm_id], result.switch_cpu_usages[pm_id], result.vhost_cpu_usages[pm_id],
            result.total_cpu_usages[pm_id])
        if pm_id in result.pms_over:
            w_str = click.style(w_str, fg='red')
            stat_str += ', over=%d' % result.pms_over[pm_id]
        elif pm_id in result.pms_under:
            w_str = click.style(w_str, fg='blue')
            stat_str += ', under=%d' % result.pms_under[pm_id]
        elif pm_id in result.pms_used:
            w_str = click.style(w_str, fg='green')
        else:
            stat_str = 'unused'
        click.echo('%s  %s %s | %s' % (indent, w_str, pm, stat_str))


def rank_result(input, result):
    """
    :param MetisInput input:
    :param PartitionResult result:
    :return:
    """
    pms_over_num = len(result.pms_over)
    if pms_over_num > 0:
        tier = 1
        pms_over_degree = 0
        for pm_id, over_shares in result.pms_over.items():
            deg = int(over_shares * 100 / result.pms_used[pm_id].max_cpu_share)
            if deg > pms_over_degree:
                pms_over_degree = deg
    else:
        tier = 0
        pms_over_degree = 0
    return ResultRank(tier=tier, pms_over=pms_over_num, pms_under=len(result.pms_under),
                      pms_used=len(result.pms_used), pms_unused=len(input.pms_unused) + len(result.pms_unused),
                      pms_over_degree=pms_over_degree, min_cut=result.min_cut)


def execute_input(graph, graph_properties, metis_input, **metis_options):
    """
    :param networkx.Graph graph:
    :param GraphProperties graph_properties:
    :param MetisInput metis_input:
    :return (ParititonResult, ResultRank):
    """
    min_cut, assignment = call_metis(graph, metis_input, **metis_options)
    result = analyze_result(graph, graph_properties, metis_input, min_cut, assignment)
    rank = rank_result(metis_input, result)
    return result, rank


def run_imbalance_vector(graph, graph_properties, base_input, i, j):
    metis_input = base_input._replace(sw_imbalance_factor=i / 100, vhost_imbalance_factor=j / 100)
    result, rank = execute_input(graph, graph_properties, metis_input)
    return metis_input, result, rank


def waterfall_branch_out(input, result, rank, result_hash):
    """
    :param MetisInput input:
    :param PartitionResult result:
    :param ResultRank rank:
    :param ResultHash result_hash:
    :return:
    """
    click.echo('Branch factors: pms_over=%d, pms_under=%d, pms_unused_by_metis=%d, pms_free=%d.' % (
        rank.pms_over, rank.pms_under, len(result.pms_unused), len(input.pms_unused)))
    if rank.pms_over > 0 and rank.pms_under == 0 and len(result.pms_unused) == 0 and len(input.pms_unused) > 0:
        # Extract the input lists.
        next_pm = input.pms_unused[0]
        pms_used = list(input.pms)
        pms_used.append(next_pm)
        if result_hash.is_pms_used_input_registered(pms_used):
            click.echo('  Branch already exists.')
            click.echo()
            return None
        # Append the next free PM to the list with default params.
        pms_unused = list(input.pms_unused)
        pms_unused.pop(0)
        sw_cpu_shares = []
        vhost_cpu_shares = []
        for pm in pms_used:
            sw_share = max(constants.INIT_SWITCH_CPU_SHARES, pm.min_switch_cpu_share)
            sw_cpu_shares.append(sw_share)
            vhost_cpu_shares.append(pm.max_cpu_share - sw_share)
        mutated_input = input._replace(pms=tuple(pms_used), pms_unused=tuple(pms_unused),
                                       seed=constants.INIT_DOMINANCE_TOLERANCE,
                                       sw_cpu_shares=tuple(sw_cpu_shares), vhost_cpu_shares=tuple(vhost_cpu_shares))
        click.secho('  New branch: {%s}.' % ','.join([str(pm.pm_id) for pm in pms_used]), fg='cyan')
        click.echo()
        return mutated_input
    click.echo()
    return None


def waterfall_adjust_shares(input, result, rank, result_store, result_hash, new_branch_created=False):
    num_pms = len(input.pms)
    switch_cpu_shares = [0] * num_pms
    vhost_cpu_shares = [0] * num_pms
    last_under_utilized_increase = -1
    dominance_allowance_count = input.seed

    # Change: We added a factor called dominance allowance. It first acts as an upper bound for how many more rounds
    # to perform when no progress is made. Secondly it's the seed value for RNG to make METIS result different given
    # same constraints.

    click.echo('Adjust shares:')

    if result_hash.is_assignment_known(result.assignment):
        dominance_allowance_count -= 2
    else:
        result_hash.register_assignment(result.assignment)

    rank_dominance_level = result_store.is_rank_dominated(rank)
    result_store.save_result(input, result, rank)

    if dominance_allowance_count > 4 and rank.pms_over == len(input.pms) and new_branch_created:
        dominance_allowance_count = 4
    elif rank_dominance_level == DominanceLevel.NO_DOMINANCE:
        dominance_allowance_count = constants.INIT_DOMINANCE_TOLERANCE
    elif rank_dominance_level == DominanceLevel.MIN_CUT_EXISTS:
        dominance_allowance_count -= 1
    else:
        # A high dominance.
        dominance_allowance_count -= 4

    if dominance_allowance_count < 0:
        click.secho(
            '  Stop exploring branch {%s}. Allowance exhausted.' % ','.join([str(pm.pm_id) for pm in input.pms]),
            fg='yellow')
        click.echo()
        return None

    total_over_utilized_shares = sum(result.pms_over.values())

    # Traverse from the PM taking most load to the one taking least load.
    for (_, pm_id) in sorted([(w, pm_id) for pm_id, w in result.share_weights.items()], reverse=True):
        total_cpu_usage = result.total_cpu_usages[pm_id]
        switch_cpu_usage = result.switch_cpu_usages[pm_id]
        vhost_cpu_usage = result.vhost_cpu_usages[pm_id]

        pm = result.pms_used[pm_id] if total_cpu_usage > 0 else result.pms_unused[pm_id]
        pm_index = input.pms.index(pm)

        if pm_id in result.pms_over:
            shares_over = result.pms_over[pm_id]
            assert(total_cpu_usage > 0)
            # Proportionally shrink current CPU usages so that they sum up to max cpu share.
            #if total_cpu_usage > 0:
            next_switch_cpu_share = min(pm.max_switch_cpu_share,
                                        max(pm.min_switch_cpu_share,
                                            int(switch_cpu_usage / total_cpu_usage * pm.max_cpu_share)))
            # else:
            #     next_switch_cpu_share = min(pm.max_switch_cpu_share,
            #                                 max(pm.min_switch_cpu_share, constants.INIT_SWITCH_CPU_SHARES))
            next_vhost_cpu_share = pm.max_cpu_share - next_switch_cpu_share
            switch_cpu_shares[pm_index] = next_switch_cpu_share
            vhost_cpu_shares[pm_index] = next_vhost_cpu_share
            click.echo('  %s: over by %d shares. sw: %d/%d -> %d. vhost: %d/%d -> %d.' % (
                       pm, shares_over, switch_cpu_usage, input.sw_cpu_shares[pm_index], next_switch_cpu_share,
                       vhost_cpu_usage, input.vhost_cpu_shares[pm_index], next_vhost_cpu_share))
        else:
            if total_over_utilized_shares > 0:
                shares_over = pm_overutilized_shares(pm, total_cpu_usage, delta=total_over_utilized_shares)
                if shares_over > 0:
                    delta = total_over_utilized_shares - shares_over
                    total_over_utilized_shares -= delta
                else:
                    delta = total_over_utilized_shares
                    total_over_utilized_shares = 0
            else:
                delta = 0
            is_under = is_pm_underutilized(pm, total_cpu_usage, delta=delta)
            # Change: for both in-range PMs and under PMs, we increase shares so that they go to in-range level.
            if is_under:
                # The PM is still under-utilized after taking the delta shares. We increase not only the delta shares,
                # but also a portion of the under shares after taking the delta.
                shares_under = pm_underutilized_shares(pm, total_cpu_usage, delta=delta) + delta
                shares_usable = max(2, shares_under)
                # shares_usable = max(2, int(shares_under * constants.PM_UNDER_UTILIZED_PORTION_ALLOC_RATIO))
                # Share increase of this PM should not exceed share increase of any previous under-utilized PM.
                if last_under_utilized_increase > 0:
                    if shares_usable > last_under_utilized_increase:
                        shares_usable = last_under_utilized_increase
                    elif shares_usable < last_under_utilized_increase:
                        last_under_utilized_increase = shares_usable
                elif last_under_utilized_increase < 0:
                    last_under_utilized_increase = shares_usable
            else:
                # The PM can well digest the delta shares and is in-range after taking the delta shares.
                shares_usable = delta
            # Proportionally allocate the allocatable shares to switch and vhost shares.
            if switch_cpu_usage > 0:
                switch_cpu_delta = min(max(1, int(shares_usable * switch_cpu_usage / total_cpu_usage)),
                                       pm.max_switch_cpu_share - switch_cpu_usage)
            else:
                total_cpu_share = input.sw_cpu_shares[pm_index] + input.vhost_cpu_shares[pm_index]
                switch_cpu_delta = min(max(1, int(shares_usable * input.sw_cpu_shares[pm_index] / total_cpu_share)),
                                       pm.max_switch_cpu_share - switch_cpu_usage)
            if switch_cpu_usage + switch_cpu_delta < pm.min_switch_cpu_share:
                switch_cpu_delta = pm.min_switch_cpu_share - switch_cpu_usage
            vhost_cpu_delta = max(0, shares_usable - switch_cpu_delta)
            switch_cpu_shares[pm_index] = switch_cpu_usage + switch_cpu_delta
            if len(result.pms_over) == num_pms:
                vhost_cpu_shares[pm_index] = pm.max_cpu_share - switch_cpu_shares[pm_index]
            else:
                vhost_cpu_shares[pm_index] = vhost_cpu_usage + vhost_cpu_delta
            if is_under:
                click.echo('  %s: under by %d(%d) shares. Alloc %d shares. '
                              'sw: %d/%d -> %d. vhost: %d/%d -> %d.' % (
                              pm, shares_under, delta, shares_usable,
                              switch_cpu_usage, input.sw_cpu_shares[pm_index], switch_cpu_shares[pm_index],
                              vhost_cpu_usage, input.vhost_cpu_shares[pm_index], vhost_cpu_shares[pm_index]))
            else:
                click.echo('  %s: ok with %d delta shares. sw: %d/%d -> %d. vhost: %d/%d -> %d.' % (
                              pm, delta,
                              switch_cpu_usage, input.sw_cpu_shares[pm_index], switch_cpu_shares[pm_index],
                              vhost_cpu_usage, input.vhost_cpu_shares[pm_index], vhost_cpu_shares[pm_index]))
    switch_cpu_shares = [int(o * (1 - constants.SHARE_ADJUSTMENT_NEW_ALPHA) + n * constants.SHARE_ADJUSTMENT_NEW_ALPHA) for o, n in zip(input.sw_cpu_shares, switch_cpu_shares)]
    vhost_cpu_shares = [int(o * (1 - constants.SHARE_ADJUSTMENT_NEW_ALPHA) + n * constants.SHARE_ADJUSTMENT_NEW_ALPHA) for o, n in zip(input.vhost_cpu_shares, vhost_cpu_shares)]
    new_input = input._replace(sw_cpu_shares=tuple(switch_cpu_shares), vhost_cpu_shares=tuple(vhost_cpu_shares),
                               seed=dominance_allowance_count)

    click.echo()
    return new_input


def waterfall_single_iteration(graph, graph_properties, input, task_queue, result_store, result_hash, executor):
    """
    :param networkx.Graph graph:
    :param GraphProperties graph_properties:
    :param MetisInput initial_input:
    :param [(MetisInput, int)] task_queue:
    :param ResultHistory result_store:
    :param ResultHash result_hash:
    :return:
    """
    click.echo('-' * 79 + '\n')
    click.echo('Input (%d in queue):' % len(task_queue))
    print_input(input, indent=2)
    click.echo()

    fut = executor.submit(execute_input, graph, graph_properties, input)
    result, rank = fut.result()

    click.echo('Result:')
    print_result_brief(result, indent=2)
    click.echo()

    branch_input = waterfall_branch_out(input, result, rank, result_hash)
    if branch_input:
        iv_store = brute_force_initial_input(graph, graph_properties, branch_input)
        result_hash.register_pm_used_input(branch_input.pms)
        task_queue.append(iv_store.best_candidates()[-1][0])

    adjust_input = waterfall_adjust_shares(input, result, rank, result_store, result_hash, branch_input is not None)
    if adjust_input:
        task_queue.append(adjust_input)

    return result, rank


def dump_result_ranks(result_store):
    lines = []
    def dump_rank(input, result, rank):
        pms_used = sorted(result.pms_used.keys())
        line = ['%.2f, %.2f' % (input.sw_imbalance_factor, input.vhost_imbalance_factor),
                ','.join([str(pm.pm_id) for pm in input.pms]),
                ','.join([str(v) for v in input.sw_cpu_shares]),
                ','.join([str(v) for v in input.vhost_cpu_shares]),
                input.seed,
                ','.join([str(v) for v in pms_used]),
                ','.join([str(result.switch_cpu_usages[i]) for i in pms_used]),
                ','.join([str(result.vhost_cpu_usages[i]) for i in pms_used]),
                '%d/%d/%d' % (rank.pms_under, rank.pms_over, rank.pms_over_degree), rank.min_cut]
        lines.append(line)
    result_store.traverse(dump_rank)
    header = ('imb_vector', 'pms_in', 'sw_shares', 'vhost_shares', 'sd',
              'pms_used', 'sw_usages', 'vhost_usages', 'u/o/d', 'min_cut')
    return tabulate.tabulate(lines, headers=header)


def waterfall_main_loop(graph, graph_properties, initial_input, output_dir=None):
    """
    :param networkx.Graph graph:
    :param GraphProperties graph_properties:
    :param MetisInput initial_input:
    :param int dominance_allowance_count:
    :return:
    """
    task_queue = []
    result_hash = ResultHash()
    result_store = ResultHistory()
    from  collections import defaultdict
    iterative_store = SerialResultHistory()
    iterative_store_by_branches = defaultdict(SerialResultHistory)

    task_queue.append(initial_input)
    result_hash.register_pm_used_input(initial_input.pms)
    with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
        while len(task_queue):
            metis_input = task_queue.pop(0)
            result, rank = waterfall_single_iteration(graph=graph, graph_properties=graph_properties,
                                                      input=metis_input, task_queue=task_queue,
                                                      result_store=result_store, result_hash=result_hash,
                                                      executor=executor)
            iterative_store.save_result(metis_input, result, rank)
            iterative_store_by_branches[tuple([pm.pm_id for pm in metis_input.pms])].save_result(metis_input, result, rank)

    click.secho('\nSequential results:\n', bold=True)
    click.echo(dump_result_ranks(iterative_store))
    click.echo()

    click.secho('\nSequential results by branches:\n', bold=True)
    for k in sorted(iterative_store_by_branches.keys()):
        click.echo(dump_result_ranks(iterative_store_by_branches[k]))
        click.echo()

    click.secho('\nResults from best to worst:\n', bold=True)
    click.echo(dump_result_ranks(result_store))
    click.echo()

    # Disabled because I haven't observed improvement for doing this in v4.
    # click.secho('Brute force imbalance vector for best result:', bold=True)
    # iv_store = brute_force_initial_input(
    #     graph, graph_properties, result_store.best_candidates()[0][0],
    #     output_filename=os.path.join(output_dir, 'find_iv_final.csv') if output_dir else None)
    # click.echo(dump_result_ranks(iv_store))

    if output_dir:
        for i, (metis_input, result, rank) in enumerate(result_store.best_candidates()):
            outfile_path = os.path.join(output_dir, 'best_assignment_%d' % i)
            with open(outfile_path + '.txt', 'w') as f:
                f.write('\n'.join([str(i) for i in result.assignment]))
            del f
            visualize_assignment(graph, result.assignment, outfile_path)
    print()


def dump_ranks(result_store, to_string_func):
    lines = [['imb_vector'] + list(ResultRank_Fields)]
    def append_to_lines(input, result, rank):
        line = ['%.2f, %.2f' % (input.sw_imbalance_factor, input.vhost_imbalance_factor)]
        line.extend(rank)
        lines.append(line)
    result_store.traverse(append_to_lines)
    return to_string_func(lines)


def dump_to_csv(lines, filepath):
    with open(filepath, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for line in lines:
            writer.writerow(line)


def brute_force_initial_input(graph, graph_properties, base_input, output_filename=None):
    """
    :param networkx.Graph graph:
    :param GraphProperties graph_properties:
    :param [models.Machine] pms:
    :return:
    """
    iter_store = SerialResultHistory()
    result_store = ResultHistory()
    all_futures = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for i in range(0, 41):
            for j in range(0, 41):
                all_futures.append(executor.submit(run_imbalance_vector, graph, graph_properties, base_input, i, j))
    concurrent.futures.wait(all_futures)
    for fut in all_futures:
        metis_input, result, rank = fut.result()
        iter_store.save_result(metis_input, result, rank)
        if result_store.is_rank_dominated(rank) in (DominanceLevel.NO_DOMINANCE, DominanceLevel.MIN_CUT_EXISTS):
            result_store.save_result(metis_input, result, rank)
    print()
    print(dump_ranks(result_store, to_string_func=functools.partial(tabulate.tabulate, headers='firstrow')))
    print()
    if output_filename:
        dump_ranks(iter_store, functools.partial(dump_to_csv, filepath=output_filename))
    return result_store


def get_initial_input(graph, graph_properties, pms, sw_imbalance_factor, vhost_imbalance_factor):
    """
    :param networkx.Graph graph:
    :param GraphProperties graph_properties:
    :param [models.Machine] pms:
    :param float sw_imbalance_factor:
    :param float vhost_imbalance_factor:
    :return MetisInput:
    """
    vhost_divisor = 100 / graph_properties.total_vhost_weight
    swcap_divisor = 100 / graph_properties.total_vertex_weight
    # Use the tightest constraint as the first key.
    total_cpu_shares = sum([pm.max_cpu_share for pm in pms])
    total_sw_caps = sum([pm.capacity_func.eval(pm.max_switch_cpu_share) for pm in pms])
    if total_cpu_shares * vhost_divisor <= total_sw_caps * swcap_divisor:
        key1 = lambda pm: pm.max_cpu_share
        key2 = lambda pm: pm.capacity_func.eval(pm.max_switch_cpu_share)
        key_order = 0
    else:
        key1 = lambda pm: pm.capacity_func.eval(pm.max_switch_cpu_share)
        key2 = lambda pm: pm.max_cpu_share
        key_order = 1
    # Sort the PMs from most powerful to least powerful.
    pms_sorted = sorted([(key1(pm), key2(pm), -pm.min_switch_cpu_share, pm.pm_id, pm) for pm in pms], reverse=True)

    total_cpu_shares = 0
    total_sw_caps = 0
    pms_used = []
    pms_free = []
    click.echo('PMs sorted by usefulness:')
    for i, (k1, k2, _, _, pm) in enumerate(pms_sorted):
        if key_order == 0:
            max_cpu_share = k1
            max_sw_cap = k2
        else:
            max_cpu_share = k2
            max_sw_cap = k1
        if total_cpu_shares <= graph_properties.total_vhost_weight or \
                   total_sw_caps < graph_properties.total_vertex_weight:
            total_cpu_shares += max_cpu_share
            total_sw_caps += max_sw_cap
            click.secho('  [%7.2f%%] [%7.2f%%] %s | max_sh=%d, max_cap=%d' % (
                total_cpu_shares * vhost_divisor, total_sw_caps * swcap_divisor, pm.full_str, max_cpu_share, max_sw_cap), fg='green')
            pms_used.append(pm)
        else:
            click.echo('  [        ] [        ] %s' % pm.full_str)
            pms_free.append(pm)
    click.echo()

    # Fill in initial share allocations.
    sw_cpu_shares = []
    vhost_cpu_shares = []
    for pm in pms_used:
        sw_cpu_share = max(constants.INIT_SWITCH_CPU_SHARES, pm.min_switch_cpu_share)
        sw_cpu_shares.append(sw_cpu_share)
        vhost_cpu_shares.append(pm.max_cpu_share - sw_cpu_share)
    return MetisInput(pms=tuple(pms_used), pms_unused=tuple(pms_free), seed=constants.INIT_DOMINANCE_TOLERANCE,
                      sw_cpu_shares=tuple(sw_cpu_shares), vhost_cpu_shares=tuple(vhost_cpu_shares),
                      sw_imbalance_factor=sw_imbalance_factor, vhost_imbalance_factor=vhost_imbalance_factor)


def print_input(metis_input, indent=0):
    """
    :param MetisInput metis_input:
    :return:
    """
    indent = ' ' * indent
    switch_cap_shares = [round(pm.capacity_func.eval(metis_input.sw_cpu_shares[i]), 2) for i, pm in enumerate(metis_input.pms)]
    norm_switch_cap_shares = normalize_shares(switch_cap_shares)
    norm_vhost_cpu_shares = normalize_shares(metis_input.vhost_cpu_shares)

    click.echo('%s<MetisInput> imb=(%.2f, %.2f), seed=%d' % (
        indent, metis_input.sw_imbalance_factor, metis_input.vhost_imbalance_factor, metis_input.seed))

    table_rows = [('PM #', 'sw_cpu', 'vh_cpu', 'sw_cap', 'sw_frac', 'vh_frac')]
    for i, pm in enumerate(metis_input.pms):
        table_rows.append((pm, metis_input.sw_cpu_shares[i], metis_input.vhost_cpu_shares[i],
                           switch_cap_shares[i],
                           round(norm_switch_cap_shares[i] * 100, 2),
                           round(norm_vhost_cpu_shares[i] * 100, 2)))
    for i, pm in enumerate(metis_input.pms_unused):
        table_rows.append((pm, '-', '-', '-', '-', '-'))
    # Note: tabulate can generate latex or HTML code.
    print(indent + tabulate.tabulate(table_rows, headers='firstrow', tablefmt='simple').replace('\n', '\n  '))


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
    parser.add_argument('--find-iv', '--find-imbalance-vector', default=False,
                        action='store_true', help='If set, brute force potentially best imbalance vector.')
    args = parser.parse_args()

    dump_args(args)
    dump_parameters()

    machines = read_pm_file(args.pm_file)
    dump_pms(machines)

    graph, graph_properties = read_graph(args.graph_file, args.vhost_cpu_file)
    print_graph_properties(graph_properties)

    # TODO: What if it decides one PM is enough initially?
    initial_input = get_initial_input(graph, graph_properties, machines,
                                      sw_imbalance_factor=args.sw_imbalance_factor,
                                      vhost_imbalance_factor=args.vhost_imbalance_factor)
    if args.find_iv and len(initial_input.pms) > 0:
        click.echo('Brute-forcing initial input with different imbalance vectors...')
        output_filename = None if args.out is None else os.path.join(args.out, 'find_iv_initial.csv')
        store = brute_force_initial_input(graph, graph_properties, initial_input, output_filename=output_filename)
        initial_input = store.best_candidates()[0][0]

    click.echo('Initial input:')
    print_input(initial_input, indent=2)
    click.echo()

    waterfall_main_loop(graph, graph_properties, initial_input, output_dir=args.out)


if __name__ == '__main__':
    main()

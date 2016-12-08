#!/usr/bin/python3

import argparse
import operator
import sys
import inform

import constants
import graph_model
import metis
import pm_model
import utils_input
from main import AssignmentRecord
from main import MachineUsageResult
from main import normalize_shares
from main import calc_switch_cpu_usage
from main import calculate_set_weights
from main import visualize_assignment


is_tty = inform.Color.isTTY(sys.stdout)
emphasize_used_pm = inform.Color('green', enable=is_tty)
emphasize_underused_pm = inform.Color('yellow', enable=is_tty)
emphasize_overused_pm = inform.Color('red', enable=is_tty)
emphasis_unused_pm = inform.Color('blue', enable=is_tty)


def nxgraph_to_metis(graph, node_weight_attr=(constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, constants.NODE_CPU_WEIGHT_KEY)):
    # graph.graph['edge_weight_attr'] = constants.EDGE_WEIGHT_KEY
    graph.graph['node_weight_attr'] = node_weight_attr
    return metis.networkx_to_metis(graph)


def gen_partition(assignment_id, assignment_title, args, graph, machines, node_weight_attr, weights,
                  total_vertex_weight, total_vhost_cpu_weight):
    assignment_title = ' %s ' % assignment_title
    print('*' * 80)
    print(assignment_title.center(80, '*'))
    print('*' * 80)
    print()

    total_machines = len(machines)
    metis_graph = nxgraph_to_metis(graph, node_weight_attr=node_weight_attr)
    min_cut, assignment = metis.part_graph(metis_graph, nparts=total_machines, tpwgts=weights, recursive=False)
    switch_cap_usage = calculate_set_weights(graph, constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, assignment)
    switch_cpu_usage = [calc_switch_cpu_usage(machines[i], c) for i, c in enumerate(switch_cap_usage)]
    vhost_cpu_usage = calculate_set_weights(graph, constants.NODE_CPU_WEIGHT_KEY, assignment)

    machine_usages = []
    for i, pm in enumerate(machines):
        machine_usage = MachineUsageResult(old_index=i, pm=pm,
                                           switch_cpu_share=switch_cpu_usage[i], vhost_cpu_share=vhost_cpu_usage[i],
                                           switch_cap_usage=switch_cap_usage[i],
                                           vhost_cpu_usage=vhost_cpu_usage[i],
                                           total_vertex_weight=total_vertex_weight,
                                           total_cpu_weight=total_vhost_cpu_weight)
        machine_usage.print()
        machine_usages.append(machine_usage)
    print()

    assignment_record = AssignmentRecord(assignment_id=assignment_id, min_cut=min_cut,
                                         machines_used=machines, machines_unused=(),
                                         switch_cpu_shares=switch_cpu_usage, vhost_cpu_shares=vhost_cpu_usage,
                                         used_cpu_shares=[u.cpu_share_used for u in machine_usages],
                                         vhost_cpu_usage=vhost_cpu_usage,
                                         assignment=assignment)

    print(assignment_record)
    print()

    if args.out is not None:
        outfile_prefix = args.out + '/assignment_' + str(assignment_id) + '_%dPMs' % total_machines
        with open(outfile_prefix + '.txt', 'w') as f:
            f.write('\n'.join([str(v) for v in assignment]) + '\n')
        # Graph files will be prefix + {.svg|.pdf}.
        visualize_assignment(graph, assignment, outfile_path=outfile_prefix)


def main():
    parser = argparse.ArgumentParser(description='A refined graph partition algorithm based on METIS.')
    parser.add_argument('-g', '--graph-file', type=str, required=True, help='File to read input graph from.')
    parser.add_argument('-p', '--pm-file', type=str, required=True, help='File to read PM information.')
    parser.add_argument('-c', '--vhost-cpu-file', type=str, required=True, help='File to read vhost CPU information.')
    parser.add_argument('-o', '--out', type=str, required=False, default=None, help='If given, will generate output files to this dir.')
    args = parser.parse_args()

    print(args)
    print()

    # Print the constant params.
    print('Program parameters:')
    for k in constants.__all__:
        print('  %s: %s' % (k, getattr(constants, k)))
    print()

    # Read graph input and vhost CPU file, and then update the graph properties.
    graph = graph_model.parse_chaco_input(args.graph_file)
    vhost_requirements = utils_input.read_int_file(args.vhost_cpu_file)
    graph_model.nxgraph_add_node_property(graph, constants.NODE_CPU_WEIGHT_KEY, vhost_requirements)
    total_vertex_weight = graph_model.nxgraph_node_property_sum(graph, constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY)
    total_vhost_cpu_weight = sum(vhost_requirements)
    print('Graph stats:')
    print('  Number of vertices:     %d' % graph.number_of_nodes())
    print('  Number of edges:        %d' % graph.number_of_edges())
    print('  Total edge weight:      %d' % graph_model.nxgraph_edge_property_sum(graph, constants.EDGE_WEIGHT_KEY))
    print('  Total vertex weight:    %d' % total_vertex_weight)
    print('  Total vhost CPU weight: %d' % total_vhost_cpu_weight)
    print()

    # Read PM input.
    machines = pm_model.Machine.read_machines_from_file(args.pm_file)
    total_machines = len(machines)
    print('Read %d PMs from input:' % total_machines)
    for p in machines:
        print('  ' + str(p))
    print()

    if total_machines == 1:
        print('No partition needed -- only one PM available.')
        sys.exit(0)

    # Generate balanced partitioning result.
    gen_partition('BALANCED', 'Weight-balanced Partitioning', args, graph, machines,
                  (constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY), normalize_shares([1] * total_machines),
                  total_vertex_weight, total_vhost_cpu_weight)

    # Partitioning according to max cpu share.
    gen_partition('MAX_CPU_SHARE', 'MAX_CPU_SHARE Partitioning', args, graph, machines,
                  (constants.NODE_CPU_WEIGHT_KEY), normalize_shares([pm.max_cpu_share for pm in machines]),
                  total_vertex_weight, total_vhost_cpu_weight)

    # Partitioning based on 60% capacity.
    gen_partition('C60_CAPACITY', 'C(60%) Partitioning', args, graph, machines,
                  (constants.NODE_CPU_WEIGHT_KEY), normalize_shares([pm.capacity_func.eval(60) for pm in machines]),
                  total_vertex_weight, total_vhost_cpu_weight)


if __name__ == '__main__':
    main()

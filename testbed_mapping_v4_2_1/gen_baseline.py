#!/usr/bin/python3

import argparse
import concurrent.futures
import functools
import json
import os

import tabulate

import constants
import metis
import models

from main import dump_args, dump_parameters, dump_pms, print_graph_properties, dump_result_ranks
from main import read_graph
from main import normalize_shares, analyze_result, print_result_brief, rank_result
from main import visualize_assignment, rank_to_dict, result_to_dict

from main import MetisInput, SerialResultHistory


def read_pm_file(filepath, normalize=False):
    machines = models.Machine.read_machines_from_file(filepath, normalize=normalize)
    return machines


def nxgraph_to_metis(graph, node_weight_attr=(constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, constants.NODE_CPU_WEIGHT_KEY)):
    # graph.graph['edge_weight_attr'] = constants.EDGE_WEIGHT_KEY
    graph.graph['node_weight_attr'] = node_weight_attr
    return metis.networkx_to_metis(graph)


def create_baseline(baseline_name, baseline_title, graph, graph_props, machines, node_weight_attr, weights):
    total_machines = len(machines)
    # metis_graph = nxgraph_to_metis(graph, node_weight_attr=node_weight_attr)
    graph.graph['node_weight_attr'] = node_weight_attr
    min_cut, assignment = metis.part_graph(graph, nparts=total_machines, tpwgts=weights, recursive=False)
    dummy_input = MetisInput(pms=machines, pms_unused=(),
                             sw_cpu_shares=[0] * total_machines, vhost_cpu_shares=[0] * total_machines,
                             seed=0, sw_imbalance_factor=1, vhost_imbalance_factor=1)
    result = analyze_result(graph, graph_props, dummy_input, min_cut, assignment)
    rank = rank_result(dummy_input, result)
    return baseline_name, baseline_title, dummy_input, result, rank


def print_baseline(graph, baseline_name, baseline_title, metis_input, result, rank, args):
    baseline_title = ' %s ' % baseline_title
    print('*' * 80)
    print(baseline_title.center(80, '*'))
    print('*' * 80)
    print()
    print_result_brief(result)
    print()
    result_store = SerialResultHistory()
    result_store.save_result(metis_input, result, rank)
    print(dump_result_ranks(result_store))
    print()
    print()
    if args.out:
        outfile_path = os.path.join(args.out, baseline_name)
        with open(outfile_path + '.txt', 'w') as f:
            f.write('\n'.join([str(i) for i in result.assignment]))
        # del f
        # visualize_assignment(graph, result.assignment, outfile_path)


def main():
    parser = argparse.ArgumentParser(description='A refined graph partition algorithm based on METIS.')
    parser.add_argument('-g', '--graph-file', type=str, required=True, help='File to read input graph from.')
    parser.add_argument('-p', '--pm-file', type=str, required=True, help='File to read PM information.')
    parser.add_argument('-c', '--vhost-cpu-file', type=str, required=True, help='File to read vhost CPU information.')
    parser.add_argument('-o', '--out', type=str, required=False, default=None,
                        help='If given, will generate output files to this dir.')
    args = parser.parse_args()

    dump_args(args)
    dump_parameters()
    
    machines_norm = read_pm_file(args.pm_file, normalize=True)
    dump_pms(machines_norm)

    machines_orig = read_pm_file(args.pm_file, normalize=False)
    dump_pms(machines_orig)

    graph, graph_properties = read_graph(args.graph_file, args.vhost_cpu_file)
    print_graph_properties(graph_properties)

    all_futures = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        all_futures.append(executor.submit(create_baseline,
                                           'BALANCED', 'Weight-balanced Partitioning',
                                           graph, graph_properties, machines_orig,
                                           constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, normalize_shares([1] * len(machines_orig))))
        all_futures.append(executor.submit(create_baseline,
                                           'MAX_CPU', 'Partitioning based on Normalized MAX_CPU_SHARE',
                                           graph, graph_properties, machines_norm,
                                           constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, normalize_shares([pm.max_cpu_share for pm in machines_norm])))
        all_futures.append(executor.submit(create_baseline,
                                           'MAX_CPU_N', 'Partitioning based on MAX_CPU_SHARE',
                                           graph, graph_properties, machines_orig,
                                           constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, normalize_shares([pm.max_cpu_share for pm in machines_orig])))
        all_futures.append(executor.submit(create_baseline,
                                           'C90', 'Partitioning based on C(90%)',
                                           graph, graph_properties, machines_orig,
                                           constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, normalize_shares([pm.capacity_func.eval(0.9 * pm.max_cpu_share) for pm in machines_orig])))
    concurrent.futures.wait(all_futures)
    data = dict()
    for fut in all_futures:
        baseline_name, baseline_title, dummy_input, result, rank = fut.result()
        print_baseline(graph, baseline_name, baseline_title, dummy_input, result, rank, args)
        data[baseline_name] = {'result': result_to_dict(result), 'rank': rank_to_dict(rank)}
    if args.out:
        with open(os.path.join(args.out, 'result') + '.json', 'w') as f:
            json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    main()

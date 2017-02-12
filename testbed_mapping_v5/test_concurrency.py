import pickle
import copy
import concurrent.futures

import os
import sys
sys.path.append(os.path.dirname(__file__) + '/networkx-metis')
import metis
import constants
import utils_input
from main import read_graph, read_pm_file, print_graph_properties, get_initial_input, normalize_shares


graph_file = 'input/graphs/1221.r0.cch.abr.graph'
pm_file = 'input/pm/pms_013_scaled_by_100.txt'
vhost_file = 'input/graphs/1221_1053rnd.host'

graph, graph_properties = read_graph(graph_file, vhost_file)
print_graph_properties(graph_properties)

pms = read_pm_file(pm_file)

base_input = get_initial_input(pms, 0.13, 0.11)


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
                                               ubvec=imbalance_vec, recursive=False, **metis_options)
        # Translate array index to PM #.
        pm_index_mapping = [pm.pm_id for pm in params.pms]
        for i, a in enumerate(assignment):
            assignment[i] = pm_index_mapping[a]
    return min_cut, tuple(assignment)


def f(i):
    # g = copy.deepcopy(graph)
    # g, graph_properties = read_graph(graph_file, vhost_file)
    min_cut, assignment = call_metis(graph, base_input, seed=0)
    return (i, min_cut, assignment)


for i in range(0, 1000):
    print(f(i))


print('*' * 79)


all_futs = []
with concurrent.futures.ProcessPoolExecutor() as executor:
    for j in range(0, 1000):
        fut = executor.submit(f, j)
        all_futs.append(fut)
r = concurrent.futures.wait(all_futs)
print(r)
for fut in all_futs:
    print(fut.result())

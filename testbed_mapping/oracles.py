#!/usr/bin/python3

import math
import os
import subprocess
import tempfile

import metis

from parse_input import to_num
from parse_chaco import parse_chaco_input
from parse_chaco import NODE_WEIGHT_KEY


SUPPORTED_ORACLES = {
    'chaco': os.path.dirname(__file__) + '/oracle_bins/Chaco-2.2/chaco'
}

NODE_CPU_KEY = 'cpu'


class BaseOracle:

    def __init__(self, work_dir=None):
        if work_dir is None:
            self.temp_work_dir = tempfile.TemporaryDirectory(suffix='chaco')
            work_dir = self.temp_work_dir.name
        elif not os.path.exists(work_dir):
            os.makedirs(work_dir, exist_ok=True)
        elif os.path.isfile(work_dir):
            raise ValueError('Working directory "%s" is a file.' % work_dir)
        self.work_dir = work_dir
        self._graph = None

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        self._graph = graph

    def update_vhost_cpu_req(self, vhost_cpu_req):
        if isinstance(vhost_cpu_req, list):
            assert(len(vhost_cpu_req) == self.graph.number_of_nodes())
            for i, v in enumerate(vhost_cpu_req):
                self.graph.node[i + 1][NODE_CPU_KEY] = v
        elif isinstance(vhost_cpu_req, dict):
            for k, v in vhost_cpu_req.items():
                self.graph.node[k][NODE_CPU_KEY] = v
        else:
            raise ValueError('Type of vhost_cpu_req is not recognized.')

    def get_assignment(self, goals):
        raise NotImplementedError('BaseOracle class must be extended.')


class ChacoOracle(BaseOracle):

    """ Chaco is a single constraint solver. """

    PARTITION_METHOD_MKL = 1
    PARTITION_METHOD_SPECTRAL = 2
    PARTITION_METHOD_INERTIAL = 3
    PARTITION_METHOD_LINEAR = 4
    PARTITION_METHOD_RANDOM = 5
    PARTITION_METHOD_SCATTERED = 6
    PARTITION_METHOD_READ_FROM_FILE = 7

    def __init__(self, graph_file_path, global_partition_method=PARTITION_METHOD_MKL, work_dir=None):
        super().__init__(work_dir)
        self.graph_file_path = graph_file_path
        self.global_partition_method = global_partition_method
        self.graph = parse_chaco_input(graph_file_path)

    def get_assignment(self, goals):
        hypercube_dimension = math.ceil(math.log(len(goals), 2))
        num_nodes_coarsened_to = 2 ** hypercube_dimension
        # Generate the goal file.
        with open(self.work_dir + '/goals', 'w') as goalf:
            print('\n'.join([str(v) for v in goals]), file=goalf)
            if len(goals) < 2 ** hypercube_dimension:
                # Append some zero goals so that the number of goal values is a
                # power of 2.
                print(
                    '0\n' * (2 ** hypercube_dimension - len(goals)), file=goalf)
        # Generate the input file for this iteration.
        oracle_input = self.graph_file_path + '\n'
        oracle_input += self.work_dir + '/goals\n'
        oracle_input += self.work_dir + '/output\n'
        oracle_input += str(self.global_partition_method) + '\n'
        oracle_input += str(num_nodes_coarsened_to) + '\n'
        oracle_input += str(hypercube_dimension) + '\n'
        oracle_input += str(hypercube_dimension) + '\nn\n'
        with open(self.work_dir + '/input', 'w') as inf:
            print(oracle_input, file=inf)
        with open(self.work_dir + '/input', 'r') as inf:
            o = subprocess.check_output([SUPPORTED_ORACLES[
                                        'chaco']], stdin=inf, timeout=10, universal_newlines=True, stderr=subprocess.STDOUT)
            print(o + '\n')
        with open(self.work_dir + '/output', 'r') as outf:
            return [to_num(v) for v in outf.readlines()]


class MetisOracle(BaseOracle):

    def __init__(self, graph_file_path, is_graph_file_chaco_format=True, work_dir=None):
        super().__init__(work_dir)
        if is_graph_file_chaco_format:
            self.graph = parse_chaco_input(graph_file_path)
        else:
            raise NotImplementedError(
                'METIS graph format is not yet implemented!')
        setattr(self.graph, 'edge_weight_attr', NODE_WEIGHT_KEY)
        setattr(self.graph, 'node_weight_attr', [NODE_WEIGHT_KEY])
        self.networkx_to_metis()

    def update_vhost_cpu_req(self, vhost_cpu_req, use_cpu_as_extra_weight=False):
        super().update_vhost_cpu_req(vhost_cpu_req)
        if use_cpu_as_extra_weight:
            setattr(self.graph, 'node_weight_attr', [NODE_WEIGHT_KEY, NODE_CPU_KEY])
        self.networkx_to_metis()

    def networkx_to_metis(self):
        self.metis_graph = metis.networkx_to_metis(self.graph)

    def _normalize_goals(self, goals):
        total_goals = sum(goals)
        new_goals = [v / total_goals for v in goals]
        if sum(new_goals) != 1.0:
            # Add the division error to the max goal set.
            new_goals[new_goals.index(max(new_goals))] += 1.0 - sum(new_goals)
        return new_goals

    def get_assignment(self, goals, goals_cpu=None, load_imbalance_vec=None):
        goal_attributes = getattr(self.graph, 'node_weight_attr')
        goals = self._normalize_goals(goals)
        if NODE_CPU_KEY in goal_attributes and goals_cpu is None:
            raise ValueError(
                'CPU share is included in vertex weight but not set in goals.')
        elif goals_cpu is not None:
            if NODE_CPU_KEY not in goal_attributes:
              print(
                  'Warning: CPU share it not a key in vertex weight. CPU goals will be ignored.')
            else:
              goals_cpu = self._normalize_goals(goals_cpu)
              goals = list(zip(goals, goals_cpu))
        
        # Build a default load imbalance vector if not given.
        if load_imbalance_vec is None:
            load_imbalance_vec = [1.0] * len(goal_attributes)

        # METIS disallows goal value to be 0. So we need to remap the values
        # to get rid of 0s.
        goals_mapping = {}
        corrected_goals = []
        for i, v in enumerate(goals):
            keep = False
            if isinstance(v, int) or isinstance(v, float):
                keep = v != 0
            else: # v is a tuple.
                keep = 0 not in v
            if keep:
                goals_mapping[len(corrected_goals)] = i
                corrected_goals.append(v)

        print(len(load_imbalance_vec))
        print(self.metis_graph.ncon.value)
        print(goals)
        print(corrected_goals)
        print(goals_mapping)
        obj_val, assignment = metis.part_graph(self.metis_graph,
                                               nparts=len(corrected_goals),
                                               tpwgts=corrected_goals,
                                               ubvec=load_imbalance_vec,
                                               recursive=False)
        assignment = [goals_mapping[v] for v in assignment]
        return assignment

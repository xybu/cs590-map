#!/usr/bin/python3

import math
import os
import subprocess
import tempfile

from parse_input import to_num
from parse_chaco import parse_chaco_input


SUPPORTED_ORACLES = {
    'chaco': os.path.dirname(__file__) + '/oracle_bins/Chaco-2.2/chaco'
}


class ChacoOracle:

    """ Chaco is a single constraint solver. """

    PARTITION_METHOD_MKL = 1
    PARTITION_METHOD_SPECTRAL = 2
    PARTITION_METHOD_INERTIAL = 3
    PARTITION_METHOD_LINEAR = 4
    PARTITION_METHOD_RANDOM = 5
    PARTITION_METHOD_SCATTERED = 6
    PARTITION_METHOD_READ_FROM_FILE = 7

    def __init__(self, graph_file_path, global_partition_method=PARTITION_METHOD_MKL, work_dir=None):
        if work_dir is None:
            self.temp_work_dir = tempfile.TemporaryDirectory(suffix='chaco')
            work_dir = self.temp_work_dir.name
        elif not os.path.exists(work_dir):
            os.makedirs(work_dir, exist_ok=True)
        elif os.path.isfile(work_dir):
            raise ValueError('Working directory "%s" is a file.' % work_dir)
        self.work_dir = work_dir
        self.global_partition_method = global_partition_method
        self.graph_file_path = graph_file_path
        self.graph = parse_chaco_input(graph_file_path)

    def get_assignment(self, goals):
        hypercube_dimension = math.ceil(math.log(len(goals), 2))
        num_nodes_coarsened_to = 2 ** hypercube_dimension
        # Generate the goal file.
        with open(self.work_dir + '/goals', 'w') as goalf:
            print('\n'.join([str(v) for v in goals]), file=goalf)
            if len(goals) < 2 ** hypercube_dimension:
                # Append some zero goals so that the number of goal values is a power of 2.
                print('0\n' * (2 ** hypercube_dimension - len(goals)), file=goalf)
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
            subprocess.check_call([SUPPORTED_ORACLES['chaco']], stdin=inf, timeout=10)
        # subp = subprocess.Popen([SUPPORTED_ORACLES['chaco']], stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        # subp.communicate(oracle_input)
        with open(self.work_dir + '/output', 'r') as outf:
            return [to_num(v) for v in outf.readlines()]

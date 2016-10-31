#!/usr/bin/python3

import networkx as nx
from parse_input import line_is_comment, to_num


def parse_metis_graph_input(file_path):
    """
    Parse a file that conforms to METIS graph input format to NetworkX object.
    METIS graph is undirected.
    Note: we are going to use a Python wrapper for METIS to achieve this.
    """
    with open(file_path, 'r') as f:
        line = f.readline().strip()
        while line_is_comment(line):
            line = f.readline().strip()
    raise NotImplementedError()

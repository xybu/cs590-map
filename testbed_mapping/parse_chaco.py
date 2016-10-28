#!/usr/bin/python3

"""
parse_chaco.py

Parse a Chaco graph file to a Networkx object.

@author Xiangyu Bu <bu1@purdue.edu>
"""

import networkx as nx
from parse_input import line_is_comment, to_num


NODE_WEIGHT_KEY = 'weight'


def parse_chaco_input(file_path):
    """ Parse an input file of Chaco format and return a NetworkX graph. """
    with open(file_path, 'r') as f:
        line = f.readline().strip()
        while line_is_comment(line):
            line = f.readline().strip()
        head = line.split()
        num_nodes = int(head[0])
        num_edges = int(head[1])
        nodes_weighted = False
        edges_weighted = False
        read_node_numbers = False
        if len(head) == 3:
            options = head[2]
            nodes_weighted = options[-1] == '1'
            edges_weighted = len(options) >= 2 and options[-2] == '1'
            read_node_numbers = len(options) == 3 and options[-3] == '1'
        G = nx.Graph()
        G.add_nodes_from(range(1, num_nodes + 1))
        i = 1
        for line in f:
            line = line.strip()
            if line_is_comment(line):
                continue
            row = [to_num(v) for v in line.split()]
            if not read_node_numbers:
                this_node = i
                neighbor_starts_at = 0
                i += 1
            else:
                this_node = row[0]
                neighbor_starts_at = 1
            if nodes_weighted:
                G.node[this_node][NODE_WEIGHT_KEY] = row[neighbor_starts_at]
                neighbor_starts_at += 1
            if not edges_weighted:
                G.add_edges_from([(this_node, node)
                                  for node in row[neighbor_starts_at:]])
            else:
                for node, weight in zip(row[neighbor_starts_at::2], row[neighbor_starts_at+1::2]):
                    G.add_edge(this_node, node, weight=weight)
        assert(num_nodes == G.number_of_nodes())
        assert(num_edges == G.number_of_edges())
        return G

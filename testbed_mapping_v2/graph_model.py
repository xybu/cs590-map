#!/usr/bin/python3

import networkx as nx

import constants
import metis
from utils_input import line_is_comment, to_num


def nxgraph_add_node_property(graph, key, values):
    """
    Update the given property of each node in the graph.
    :param networkx.Graph graph:
    :param str key:
    :param list[int | float] values:
    """
    for i, v in enumerate(values):
        # In Chaco graph foramt, vertex index starts from 1, not 0.
        graph.node[i + 1][key] = v


def nxgraph_node_property_sum(graph, key):
    """
    :param networkx.Graph graph:
    :param str key:
    :return int | float:
    """
    total = 0
    for v in graph.nodes_iter(data=True):
        total += v[1][key]
    return total


def nxgraph_edge_property_sum(graph, key):
    """
    :param networkx.Graph graph:
    :param str key:
    :return int | float:
    """
    total = 0
    for e in graph.edges_iter(data=True):
        f, t, d = e
        total += d[key]
    return total


def nxgraph_to_metis(graph):
    # graph.graph['edge_weight_attr'] = constants.EDGE_WEIGHT_KEY
    graph.graph['node_weight_attr'] = [constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, constants.NODE_CPU_WEIGHT_KEY]
    return metis.networkx_to_metis(graph)


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
        nxgraph = nx.Graph(edge_weight_attr=constants.EDGE_WEIGHT_KEY)
        nxgraph.add_nodes_from(range(1, num_nodes + 1))
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
                nxgraph.node[this_node][constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY] = row[neighbor_starts_at]
                neighbor_starts_at += 1
            if not edges_weighted:
                nxgraph.add_edges_from([(this_node, node) for node in row[neighbor_starts_at:]])
            else:
                for node, weight in zip(row[neighbor_starts_at::2], row[neighbor_starts_at+1::2]):
                    nxgraph.add_edge(this_node, node, weight=weight)
        assert(num_nodes == nxgraph.number_of_nodes())
        assert(num_edges == nxgraph.number_of_edges())
        return nxgraph

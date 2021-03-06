#!/usr/bin/python3

"""
visualize_chaco.py

Parse a Chaco graph file to a Networkx object, visualize it using matplotlib,
and optionally save it to a PNG/PDF/SVG file.

In the graph, darker color indicates higher degree and larger circle
indicates larger weight.

@author Xiangyu Bu <bu1@purdue.edu>
"""

import argparse
import math
import networkx as nx
import matplotlib.pyplot as plt


NODE_DEFAULT_WEIGHT = 50
NODE_WEIGHT_KEY = 'weight'
SUPPORTED_SAVE_FORMAT = ('pdf', 'png', 'svg')


def line_is_comment(line):
    """ Determine if a line is comment according to Chaco input spec. """
    return len(line) == 0 or line[0] in ('%', '#')


def to_num(str):
    """ Try parsing the given string to int or float. """
    try:
        return int(str)
    except:
        return float(str)


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


def main():
    parser = argparse.ArgumentParser(
        description='Parse a graph input of Chaco format and visualize it.')
    parser.add_argument(
        'path', metavar='path', type=str, help='Path to the Chaco graph input.')
    parser.add_argument('--save', metavar='format', type=str, default=None,
                        help='Save the image in the specified format (png, svg, pdf). Do not save if not specified.')
    parser.add_argument('--no-show', '-n', default=False, action='store_true',
						help='If present, only save the plot and do not show it in a new window.')
    args = parser.parse_args()
    if args.save is not None and args.save.lower() not in SUPPORTED_SAVE_FORMAT:
        raise Exception('Error: unsupported save format "%s".' % args.save)
    graph = parse_chaco_input(args.path)
    print(graph.degree())
    degrees = list(graph.degree().values())
    max_degree = max(degrees)
    # The larger the degree, the darker the node.
    degrees = [max_degree - v for v in degrees]

    try:
        weights = [n[1][NODE_WEIGHT_KEY] for n in graph.nodes(data=True)]
        sizes = [math.pow(w, 0.55) * 6 for w in weights]
    except KeyError:
        weights = NODE_DEFAULT_WEIGHT
        sizes = weights

    try:
        edge_weights = [math.log(w) / 2.4 for (u, v, w) in graph.edges(data='weight')]
        print(edge_weights)
    except:
        edge_weights = 1

    fig = plt.figure()
    # plt.title("Visualization of \"%s\"" % args.path, {'fontweight': 'bold'})
    plt.axis('off')
    pos = nx.nx_agraph.graphviz_layout(graph)

    nx.draw_networkx_nodes(graph, pos,
        node_size=sizes, node_color=degrees, cmap=plt.get_cmap('plasma'), alpha=0.95)
    nx.draw_networkx_edges(graph, pos, width=edge_weights, alpha=0.7)

    # nx.draw(graph, pos, with_labels=False, node_color=degrees, node_size=weights, cmap=plt.get_cmap('viridis'))
    fig.tight_layout()
    if args.save is not None:
        plt.savefig(args.path + '.' + args.save, transparent=True,
                    bbox_inches='tight', format=args.save, pad_inches=-0.4)
    if not args.no_show:
    	plt.show()


if __name__ == '__main__':
    main()

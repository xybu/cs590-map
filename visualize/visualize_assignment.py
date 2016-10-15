#!/usr/bin/python3

import sys
import networkx as nx
import matplotlib.pyplot as plt
from visualize_chaco import parse_chaco_input


def main():
    graph_input = sys.argv[1]
    assignment_input = sys.argv[2]
    graph = parse_chaco_input(graph_input)
    
    degrees = list(graph.degree().values())
    degrees = [v * 15 for v in degrees]
    
    with open(assignment_input, 'r') as f:
        assignment = [int(v) for v in f.readlines()]

    try:
        edge_weights = [w/10 for (u, v, w) in graph.edges(data='weight')]
        print(edge_weights)
    except:
        edge_weights = 1

    assert(len(assignment) == graph.number_of_nodes())

    plt.figure(figsize=(12, 9))
    plt.title("Visualization of Assignment of \"%s\"" % sys.argv[1], {'fontweight': 'bold'})
    plt.axis('off')
    pos=nx.nx_agraph.graphviz_layout(graph)
    nx.draw_networkx_nodes(graph, pos, node_size=degrees, node_color=assignment, cmap=plt.get_cmap('viridis'), alpha=0.95)
    nx.draw_networkx_edges(graph, pos, width=edge_weights, alpha=0.7)
    if len(sys.argv) > 3:
        plt.savefig(sys.argv[1] + '.assignment.' + sys.argv[3], transparent=True, bbox_inches='tight', format=sys.argv[3])
    plt.show()


if __name__ == '__main__':
    main()

#!/usr/bin/python3

import sys
import networkx as nx
import matplotlib.pyplot as plt
from visualize_chaco import parse_chaco_input


def visualize_assignment(graph,
                         assignment, assignment_id=None, save_format=None):
    assert(graph.number_of_nodes() == len(assignment))

    degrees = [v * 15 for v in list(graph.degree().values())]

    try:
        edge_weights = [w/10 for (u, v, w) in graph.edges(data='weight')]
        print(edge_weights, file=sys.stderr)
    except:
        edge_weights = 1

    if assignment_id is None:
        assignment_title = 'Assignment'
        assignment_suffix = '.assignment.'
    else:
        assignment_title = 'Assignment ' + str(assignment_id)
        assignment_suffix = ('.assignment_%04d' % assignment_id) + '.'

    plt.figure(figsize=(12, 9))
    plt.title("Visualization of %s of \"%s\"" %
              (assignment_title, sys.argv[1]), {'fontweight': 'bold'})
    plt.axis('off')
    pos = nx.nx_agraph.graphviz_layout(graph)
    nx.draw_networkx_nodes(graph, pos,
                           node_size=degrees,
                           node_color=assignment,
                           cmap=plt.get_cmap('viridis'),
                           alpha=0.95)
    nx.draw_networkx_edges(graph, pos, width=edge_weights, alpha=0.7)
    if save_format is not None and save_format.lower() in ('pdf', 'svg', 'png'):
        plt.savefig(sys.argv[1] + assignment_suffix + save_format,
                    transparent=True,
                    bbox_inches='tight',
                    format=save_format.lower())
    # if show_plot:
    #     plt.show()
    plt.close()


def main():
    graph_input = sys.argv[1]
    assignment_input = sys.argv[2]

    graph = parse_chaco_input(graph_input)
    past_assignments = dict()

    with open(assignment_input, 'r') as f:
        for line in f:
            all_numbers = [int(v) for v in line.strip().split(',')]
            assignment_id = all_numbers[0]
            assignment = all_numbers[1:]
            assignment_key = line.split(',', maxsplit=1)[1]
            if assignment_key in past_assignments:
                print('Assignment %d is the same as assignment %d. Skipped.' % (
                    assignment_id, past_assignments[assignment_key]))
            else:
                save_format = sys.argv[3] if len(sys.argv) > 3 else None
                past_assignments[assignment_key] = assignment_id
                visualize_assignment(
                    graph, assignment, assignment_id, save_format)

    # plt.show()


if __name__ == '__main__':
    main()

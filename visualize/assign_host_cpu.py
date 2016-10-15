#!/usr/bin/python3

import sys
from visualize_chaco import parse_chaco_input


def main():
    graph = parse_chaco_input(sys.argv[1])
    degree_of_nodes = graph.degree()
    # print(max(graph.degree().values()))
    # print(sum(graph.degree().values()))
    assignment = dict()
    for i in range(1, graph.number_of_nodes() + 1):
        if degree_of_nodes[i] < 10:
            assignment[i] = 1
        elif degree_of_nodes[i] < 25:
            assignment[i] = 3
        elif degree_of_nodes[i] < 40:
            assignment[i] = 5
        else:
            assignment[i] = 7
        print(assignment[i])
    # print(sum(assignment.values()))


if __name__ == '__main__':
    main()

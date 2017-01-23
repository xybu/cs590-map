#!/usr/bin/python3

import random
import sys
from visualize_chaco import parse_chaco_input


def main():
    graph = parse_chaco_input(sys.argv[1])
    target_cpu_weight = int(sys.argv[2])
    outfile = sys.argv[3] if len(sys.argv) == 4 else None
    degree_of_nodes = graph.degree()
    max_degree = max(graph.degree().values())
    sum_degree = sum(graph.degree().values())
    print('Target sum: ' + str(target_cpu_weight))
    print('Max degree: ' + str(max_degree))
    print('Sum degree: ' + str(sum_degree))
    print('-' * 80)
    assignment = dict()
    for i in range(1, graph.number_of_nodes() + 1):
        # if degree_of_nodes[i] < 10:
        #     assignment[i] = 1
        # elif degree_of_nodes[i] < 25:
        #     assignment[i] = 3
        # elif degree_of_nodes[i] < 40:
        #     assignment[i] = 5
        # else:
        #     assignment[i] = 7
        assignment[i] = int(target_cpu_weight * degree_of_nodes[i] / sum_degree)
        assignment[i] += random.choice((0, 0, 0, -1, 1, 1, 2))
        if assignment[i] < 0:
            assignment[i] = 0
        print('%d: %d -> %d' % (i, degree_of_nodes[i], assignment[i]))
    sum_assignment = sum(assignment.values())
    print(sum_assignment)
    if outfile is not None:
	    with open(outfile + '.%d.host' % sum_assignment, 'w') as f:
	    	for i in range(1, graph.number_of_nodes() + 1):
	    		print(assignment[i], file=f)


if __name__ == '__main__':
    main()

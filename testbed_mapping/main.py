#!/usr/bin/python3

import argparse
import math

import goal
import oracles
import parse_input


PM_SW_CPU_UPDATE_RATIO = 0.6


def calculate_vhost_cpu_dist(graph, assignment, num_pms):
    pm_vhost_cpu_usage = [0] * num_pms
    for i, pm in enumerate(assignment):
        vhost_cpu_req = graph.node[i + 1][oracles.NODE_CPU_KEY]
        pm_vhost_cpu_usage[pm] += vhost_cpu_req
    return pm_vhost_cpu_usage


def find_least_stressed_pm(num_pms, goal_values, switch_cpu_dist, vhost_cpu_dist):
    pm_cpu_usage = sorted([(switch_cpu_dist[i] + vhost_cpu_dist[i], i) for i in range(num_pms) if goal_values[i] >= 1])
    return pm_cpu_usage[0][1]


def move_vhosts_out_of_disabled_pms(graph, assignment, num_pms, goal_values, switch_cpu_dist, vhost_cpu_dist):
    print('Moving vhosts out of disabled PMs...')
    for i, pm in enumerate(assignment):
        if goal_values[pm] < 1:
            # This PM is disabled. Move it to the least stressed node.
            new_pm = find_least_stressed_pm(num_pms, goal_values, switch_cpu_dist, vhost_cpu_dist)
            vhost_cpu_req = graph.node[i + 1][oracles.NODE_CPU_KEY]
            assignment[i] = new_pm
            vhost_cpu_dist[new_pm] += vhost_cpu_req
            print('  Moved vhost %d from disabled PM #%d to PM #%d.' % (i, pm, new_pm))
            # Should have updated switch CPU usage of the PM as well to better find the least stressed PM.


def main_loop(oracle, physical_machines):
    assignment_history = []
    switch_cpu_dist = [goal.MIN_CPU_PERCENT] * len(physical_machines)
    vhost_cpu_dist = [goal.MAX_CPU_PERCENT - v for v in switch_cpu_dist]
    goal_calc = goal.GoalCalculator(oracle.graph, physical_machines)
    while True:
        print('\n' + '*' * 80 + '\n')
        goal_values = goal_calc.get_next_goal(switch_cpu_dist, vhost_cpu_dist)
        assignment = oracle.get_assignment(goal_values)
        new_vhost_cpu_dist = calculate_vhost_cpu_dist(oracle.graph, assignment, len(physical_machines))
        move_vhosts_out_of_disabled_pms(oracle.graph, assignment, len(physical_machines), goal_values, switch_cpu_dist, new_vhost_cpu_dist)
        print(assignment)
        print('\nUpdate CPU allocation for PMs...')
        for i in range(len(physical_machines)):
            if goal_values[i] < 1:
                print(' PM #%d: disabled.' % (i))
                continue
            old_switch_cpu_val = switch_cpu_dist[i]
            new_switch_cpu_val = max(goal.MIN_CPU_PERCENT, goal.MAX_CPU_PERCENT - new_vhost_cpu_dist[i])
            switch_cpu_dist[i] = math.ceil((1 - PM_SW_CPU_UPDATE_RATIO) * switch_cpu_dist[i] + PM_SW_CPU_UPDATE_RATIO * new_switch_cpu_val)
            vhost_cpu_dist[i] = goal.MAX_CPU_PERCENT - switch_cpu_dist[i]
            print(' PM #%d: vhost_CPU=%d, total=%d, next_sw_CPU=(%.2lf*%d)+(%.2lf*%d)=%d, next_vhost_CPU = %d.' % (i, new_vhost_cpu_dist[i], old_switch_cpu_val+new_vhost_cpu_dist[i], (1 - PM_SW_CPU_UPDATE_RATIO), old_switch_cpu_val, PM_SW_CPU_UPDATE_RATIO, new_switch_cpu_val, switch_cpu_dist[i], vhost_cpu_dist[i]))
        if assignment in assignment_history:
            print('Assignment result repeats round %d. Stop.' % (assignment_history.index(assignment)))
            break
        assignment_history.append(assignment)


def main():
    parser = argparse.ArgumentParser(description='Wrapper to graph partitioning oracle.')
    parser.add_argument('--oracle', type=str, default='chaco', help='Graph partitioning oracle.')
    parser.add_argument('--graph-file', type=str, required=True, help='File to read input graph from.')
    parser.add_argument('--vhost-cpu-file', type=str, required=True,
                        help='File to read CPU share of vhosts from. Line i is CPU share needed by vhost i.')
    parser.add_argument('--pm-file', type=str, required=True,
                        help='File to read PM information. One capacity function per line.')
    parser.add_argument('--work-dir', type=str, default=None,
                        help='Directory to save output files.')
    args = parser.parse_args()

    if args.oracle.lower() == 'chaco':
        oracle = oracles.ChacoOracle(args.graph_file, work_dir=args.work_dir)
    else:
        raise ValueError('Oracle "%s" is not supported.' % args.oracle)
    oracle.update_vhost_cpu_req(parse_input.read_flat_ints(args.vhost_cpu_file))

    physical_machines = parse_input.parse_pms(args.pm_file)

    main_loop(oracle, physical_machines)


if __name__ == '__main__':
    main()

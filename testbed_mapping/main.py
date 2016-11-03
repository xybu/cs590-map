#!/usr/bin/python3

import argparse
import math
import sys

import goal
import oracles
import parse_input


# The coefficient for calculating next-round switch CPU usage of PMs. Next = (1-C)*accumulated + C*current
PM_SW_CPU_UPDATE_RATIO = 0.3

# The lower bound for max CPU value of PMs if adaptively reduced.
PM_CPU_CEILING_LOW_THRESHOLD = 50

# By how much to adjust the max CPU value of PMs at each step.
PM_CPU_CEILING_ADJUST_STEP = -1


def calculate_vhost_cpu_dist(graph, assignment, num_pms):
    max_pm_id_returned = max(assignment)
    pm_vhost_cpu_usage = [0] * (max_pm_id_returned + 1)
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
        if len(goal_values) <= pm or goal_values[pm] < 1:
            # This PM is disabled. Move it to the least stressed node.
            new_pm = find_least_stressed_pm(num_pms, goal_values, switch_cpu_dist, vhost_cpu_dist)
            vhost_cpu_req = graph.node[i + 1][oracles.NODE_CPU_KEY]
            assignment[i] = new_pm
            vhost_cpu_dist[new_pm] += vhost_cpu_req
            print('  Moved vhost %d from disabled PM #%d to PM #%d.' % (i, pm, new_pm))
            # Should have updated switch CPU usage of the PM as well to better find the least stressed PM.


def main_loop(oracle, physical_machines,
              use_knapsack_limit=True,
              use_adaptive_pm_cpu_ceiling=True,
              correct_goals_by_scaling=False,
              stop_when_no_under_utilized_pms=False):
    num_pms = len(physical_machines)
    assignment_history = []
    switch_cpu_dist = [goal.INITIAL_CPU_PERCENT] * num_pms
    vhost_cpu_dist = [goal.MAX_CPU_PERCENT - v for v in switch_cpu_dist]
    pm_cpu_ceiling = [goal.MAX_CPU_PERCENT] * num_pms
    if correct_goals_by_scaling:
        correction_approach = goal.GoalCalculator.CORRECTION_APPROACH_SCALE
    else:
        correction_approach = goal.GoalCalculator.CORRECTION_APPROACH_REDUCE
    goal_calc = goal.GoalCalculator(oracle.graph, physical_machines, use_knapsack_limit, correction_approach=correction_approach)
    # prev_under_utilized_pms = []
    # prev_over_utilized_pms = []
    # pm_cpu_ceiling_adjusted_flags = [0] * num_pms
    while True:
        print('\n' + '*' * 80 + '\n')
        under_utilized_pms = []
        over_utilized_pms = []
        goal_values = goal_calc.get_next_goal(switch_cpu_dist, vhost_cpu_dist)
        assignment = oracle.get_assignment(goal_values)
        new_vhost_cpu_dist = calculate_vhost_cpu_dist(oracle.graph, assignment, num_pms)
        move_vhosts_out_of_disabled_pms(oracle.graph, assignment, num_pms, goal_values, switch_cpu_dist, new_vhost_cpu_dist)
        print('\nAssignment result:\n' + str(assignment))
        print('\nUpdate CPU allocation for PMs...')
        for i in range(num_pms):
            if goal_values[i] < 1:
                print(' PM #%d: disabled.' % (i))
                continue
            old_switch_cpu_val = switch_cpu_dist[i]
            new_vhost_cpu_val = new_vhost_cpu_dist[i]
            new_switch_cpu_val = max(goal.MIN_CPU_PERCENT, goal.MAX_CPU_PERCENT - new_vhost_cpu_val)
            total_cpu_usage = old_switch_cpu_val + new_vhost_cpu_val
            if total_cpu_usage < goal.UNDER_UTILIZED_CPU_THRESHOLD:
                status = 'under'
                under_utilized_pms.append((physical_machines[i], new_vhost_cpu_val))
            elif total_cpu_usage > goal.OVER_UTILIZED_CPU_THRESHOLD:
                status = 'over'
                record = (physical_machines[i], new_switch_cpu_val)
                over_utilized_pms.append(record)
                # if use_adaptive_pm_cpu_ceiling and record in prev_over_utilized_pms:
                #     if pm_cpu_ceiling_adjusted_flags[i] == 1:
                #         pm_cpu_ceiling[i] = max(PM_CPU_CEILING_LOW_THRESHOLD, pm_cpu_ceiling[i] + PM_CPU_CEILING_ADJUST_STEP)
                #     pm_cpu_ceiling_adjusted_flags[i] = 1 - pm_cpu_ceiling_adjusted_flags[i]
            else:
                status = 'ok'
            switch_cpu_dist[i] = math.ceil((1 - PM_SW_CPU_UPDATE_RATIO) * switch_cpu_dist[i] + PM_SW_CPU_UPDATE_RATIO * new_switch_cpu_val)
            vhost_cpu_dist[i] = pm_cpu_ceiling[i] - switch_cpu_dist[i]
            # if use_adaptive_pm_cpu_ceiling:
            #     if vhost_cpu_dist[i] <= 0:
            #         pm_cpu_ceiling[i] = goal.MAX_CPU_PERCENT
            #         vhost_cpu_dist[i] = pm_cpu_ceiling[i] - switch_cpu_dist[i]
            print(' PM #%d: %s, CPU=%d/%d/%d, next_sw_CPU=(%.2lf*%d)+(%.2lf*%d)=%d, next_vhost_CPU = %d.' % (i, status, new_vhost_cpu_val, old_switch_cpu_val+new_vhost_cpu_dist[i], pm_cpu_ceiling[i], (1 - PM_SW_CPU_UPDATE_RATIO), old_switch_cpu_val, PM_SW_CPU_UPDATE_RATIO, new_switch_cpu_val, switch_cpu_dist[i], vhost_cpu_dist[i]))
        num_over_utilized_pms = len(over_utilized_pms)
        num_under_utilized_pms = len(under_utilized_pms)
        # For adaptive reduction, we reduce *the most stressed* PM when *same thing happens again*.
        if num_under_utilized_pms <= goal.UNDER_UTILIZED_PM_ALLOWED and num_over_utilized_pms == 0:
            print('Assignment seems very nice. Stop.')
            break
        elif num_over_utilized_pms == num_pms:
            print('All PMs are over-utilized. Stop because we probably cannot do better.')
            break
        elif stop_when_no_under_utilized_pms and num_under_utilized_pms == 0:
            print('PMs are either ok or over. There might be space for balancing load but...')
            break
        elif assignment in assignment_history:
            print('Assignment result repeats round %d.' % (assignment_history.index(assignment)))
            if not use_adaptive_pm_cpu_ceiling:
                break
        assignment_history.append(assignment)
        prev_over_utilized_pms = over_utilized_pms
        prev_under_utilized_pms = under_utilized_pms
        print(pm_cpu_ceiling)
    print('\nMain loop finished with %d iterations.' % len(assignment_history))


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
    parser.add_argument('--disable-knapsack-limit', default=False, action='store_true',
                        help='If present, will not use knapsack limit when computing capacity.')
    parser.add_argument('--disable-adaptive-pm-cpu-ceiling', default=False, action='store_true',
                        help='If present, will not adaptively reduce CPU ceiling value for PMs.')
    parser.add_argument('--stop-if-no-under-pms', default=False, action='store_true',
                        help='If present, will stop when there is no PM that is under-utilized.')
    parser.add_argument('--correct-goals-by-scaling', default=False, action='store_true',
                        help='If present, will scale the goals to vertex weight sum rather than subtracting.')
    args = parser.parse_args()

    if args.oracle.lower() == 'chaco':
        oracle = oracles.ChacoOracle(args.graph_file, work_dir=args.work_dir)
    elif args.oracle.lower() == 'metis':
        oracle = oracles.MetisOracle(args.graph_file, work_dir=args.work_dir)
    else:
        raise ValueError('Oracle "%s" is not supported.' % args.oracle)
    oracle.update_vhost_cpu_req(parse_input.read_flat_ints(args.vhost_cpu_file))

    physical_machines = parse_input.parse_pms(args.pm_file)

    main_loop(oracle=oracle,
              physical_machines=physical_machines,
              use_knapsack_limit=not args.disable_knapsack_limit,
              use_adaptive_pm_cpu_ceiling=not args.disable_adaptive_pm_cpu_ceiling,
              correct_goals_by_scaling=args.correct_goals_by_scaling,
              stop_when_no_under_utilized_pms=args.stop_if_no_under_pms)


if __name__ == '__main__':
    main()

#!/usr/bin/python3

from oracles import NODE_CPU_KEY
from parse_chaco import NODE_WEIGHT_KEY
from knapsack import knapsack, knapsack_max_value

# Scale up or down the goal array to fit the target sum.
SUPPORTED_CORRECT_GOAL_APPROACH_SCALE = 0

# Use the k largest values (and reduce the kth largest one if necessary) to fit the target sum.
SUPPORTED_CORRECT_GOAL_APPROACH_REDUCE = 1

MIN_CPU_PERCENT = 10
MAX_CPU_PERCENT = 100

UNDER_UTILIZED_CPU_THRESHOLD = 90
OVER_UTILIZED_CPU_THRESHOLD = 110

USE_KNAPSACK_LIMIT = True
USE_CORRECT_GOAL_APPROACH = SUPPORTED_CORRECT_GOAL_APPROACH_REDUCE


def scale_array_to_target_sum(data, target_sum):
    print('Scaling array by %lfX to meet target %.3lf.' % (target_sum / sum(data), target_sum))
    data = [v / sum(data) * target_sum for v in data.copy()]
    if sum(data) != target_sum:
        diff = target_sum - sum(data)
        data[0] += diff
    return data


def reduce_array_to_target_sum(data, target_sum):
    print('Keeping the first K\' elements that sum up to %.3lf' % target_sum)
    result = [0] * len(data)
    data = sorted(enumerate(data), key=lambda x: x[1])[::-1] # Sort the data by value.
    for i, v in data:
        if v >= target_sum:
            result[i] = target_sum
            target_sum = 0
        else:
            result[i] = v
            target_sum -= v
    return result


class GoalCalculator:

    def __init__(self, graph, pms):
        """
        :param networkx.Graph graph:
        :param list[pms.PhysicalMachine] pms:
        """
        self.graph = graph
        self.pms = pms
        self.goal_hist = []
        self.switch_cpu_hist = []
        self.vhost_cpu_hist = []
        self.sum_of_node_weight = 0
        self.sum_of_node_cpu = 0
        if USE_KNAPSACK_LIMIT:
            self._vhost_cpu_req = []
            self._vhost_weight = []
        for node in graph.nodes(data=True):
            node_cpu = node[1][NODE_CPU_KEY]
            node_weight = node[1][NODE_WEIGHT_KEY]
            if USE_KNAPSACK_LIMIT:
                self._vhost_cpu_req.append(node_cpu)
                self._vhost_weight.append(node_weight)
            self.sum_of_node_weight += node_weight
            self.sum_of_node_cpu += node_cpu

    def get_next_goal(self, switch_cpu_dist, vhost_cpu_dist):
        print('Calculating goal for round %d...' % len(self.goal_hist))
        self.switch_cpu_hist.append(switch_cpu_dist.copy())
        self.vhost_cpu_hist.append(vhost_cpu_dist.copy())
        pm_capacity = []
        for i, pm in enumerate(self.pms):
            func_cap = pm.capacity_func.eval(switch_cpu_dist[i])
            if USE_KNAPSACK_LIMIT:
                ks_cap = knapsack_max_value(knapsack(self._vhost_weight, self._vhost_cpu_req, vhost_cpu_dist[i]))
                cap = min(func_cap, ks_cap)
                print("  PM #%d: func_cap=%lf, ks_cap=%lf. Choose %lf." % (pm.pm_id, func_cap, ks_cap, cap))
                pm_capacity.append(cap)
            else:
                print("  PM #%d: Use func_cap=%lf." % (pm.pm_id, func_cap))
        if sum(pm_capacity) < self.sum_of_node_weight:
            # Max possible capacity is less than node weight, scale the values up proportionally.
            pm_capacity = scale_array_to_target_sum(pm_capacity, self.sum_of_node_weight)
        elif sum(pm_capacity) > self.sum_of_node_weight:
            # Max possible capacity is too large.
            if USE_CORRECT_GOAL_APPROACH == SUPPORTED_CORRECT_GOAL_APPROACH_SCALE:
                pm_capacity = scale_array_to_target_sum(pm_capacity, self.sum_of_node_weight)
            elif USE_CORRECT_GOAL_APPROACH == SUPPORTED_CORRECT_GOAL_APPROACH_REDUCE:
                pm_capacity = reduce_array_to_target_sum(pm_capacity, self.sum_of_node_weight)
            else:
                raise ValueError('Constant USE_CORRECT_GOAL_APPROACH has unsupported value.')
        print('Will use the following goal values:')
        for i, c in enumerate(pm_capacity):
            print('  goal[%d] = %lf' % (i, c))
        print()
        self.goal_hist.append(pm_capacity.copy())
        return pm_capacity

#!/usr/bin/python3

import argparse
import sys
import inform

import constants
import graph_model
import metis
import pm_model
import utils_input


is_tty = inform.Color.isTTY(sys.stdout)
emphasize_used_pm = inform.Color('green', enable=is_tty)
emphasize_underused_pm = inform.Color('yellow', enable=is_tty)
emphasize_overused_pm = inform.Color('red', enable=is_tty)
emphasis_unused_pm = inform.Color('blue', enable=is_tty)


def underline(s):
    return '\033[4m' + s + '\033[0m' if is_tty else s


def normalize_shares(shares):
        total = sum(shares)
        norm_shares = [v / total for v in shares]
        if sum(norm_shares) != 1:
            # Add the division error to the max goal set.
            norm_shares[norm_shares.index(max(norm_shares))] += 1 - sum(norm_shares)
        return norm_shares


def calculate_set_weights(graph, key, assignment):
    max_pm_id_returned = max(assignment)
    set_weights = [0] * (max_pm_id_returned + 1)
    for i, pm in enumerate(assignment):
        set_weights[pm] += graph.node[i + 1][key]
    return set_weights


class AssignmentRecord:

    def __init__(self, assignment_id, min_cut, machines_used, machines_unused, switch_cpu_shares, vhost_cpu_shares, used_cpu_shares, vhost_cpu_usage, assignment):
        self.assignment_id = assignment_id
        self.min_cut = min_cut
        self.machines_used = machines_used
        self.machines_unused = machines_unused
        self.switch_cpu_shares = switch_cpu_shares
        self.vhost_cpu_shares = vhost_cpu_shares
        self.used_cpu_shares = used_cpu_shares
        self.vhost_cpu_usage = vhost_cpu_usage
        self.assignment = assignment

    def __repr__(self):
        s = underline('Assignment %d\n' % self.assignment_id)
        s += '  Min cut: %d\n' % self.min_cut
        s += '  Machines used:\n'
        for i, pm in enumerate(self.machines_used):
            if self.used_cpu_shares[i] > pm.max_cpu_share * (1 + constants.PM_OVER_UTILIZED_THRESHOLD):
                f = emphasize_overused_pm
            elif self.used_cpu_shares[i] < pm.max_cpu_share * (1 - constants.PM_UNDER_UTILIZED_THRESHOLD):
                f = emphasize_underused_pm
            else:
                f = emphasize_used_pm
            s += '    ' + f(pm) + '\n'
            s += '      CPU: switch_sh=%d, vhost={u=%d, sh=%d}, total={u=%d, sh=%d}.\n' % (self.switch_cpu_shares[i], self.vhost_cpu_usage[i], self.vhost_cpu_shares[i], self.used_cpu_shares[i], self.switch_cpu_shares[i] + self.vhost_cpu_shares[i])
        s += '  Machines excluded:\n'
        for pm in self.machines_unused:
            s += '    ' + emphasis_unused_pm(pm) + '\n'
        s += '  Assignment of nodes:\n    '
        for i, v in enumerate(self.assignment):
            s += str(v) + ', '
            if i % 20 == 19:
                s += '\n    '
        return s.strip()

    @staticmethod
    def cmp_key(a):
        return a.min_cut


def main():
    parser = argparse.ArgumentParser(description='A refined graph partition algorithm based on METIS.')
    parser.add_argument('-g', '--graph-file', type=str, required=True, help='File to read input graph from.')
    parser.add_argument('-p', '--pm-file', type=str, required=True, help='File to read PM information.')
    parser.add_argument('-c', '--vhost-cpu-file', type=str, required=True, help='File to read vhost CPU information.')
    args = parser.parse_args()

    print(args)
    print()

    # Read graph input and vhost CPU file, and then update the graph properties.
    graph = graph_model.parse_chaco_input(args.graph_file)
    vhost_requirements = utils_input.read_int_file(args.vhost_cpu_file)
    graph_model.nxgraph_add_node_property(graph, constants.NODE_CPU_WEIGHT_KEY, vhost_requirements)
    total_vertex_weight = graph_model.nxgraph_node_property_sum(graph, constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY)
    total_vhost_cpu_weight = sum(vhost_requirements)
    print('Graph stats:')
    print('  Number of vertices:     %d' % graph.number_of_nodes())
    print('  Number of edges:        %d' % graph.number_of_edges())
    print('  Total edge weight:      %d' % graph_model.nxgraph_edge_property_sum(graph, constants.EDGE_WEIGHT_KEY))
    print('  Total vertex weight:    %d' % total_vertex_weight)
    print('  Total vhost CPU weight: %d' % total_vhost_cpu_weight)
    print()

    # Obtain the graph object used for METIS API.
    metis_graph = graph_model.nxgraph_to_metis(graph)

    # Read PM input.
    machines = pm_model.Machine.read_machines_from_file(args.pm_file)
    total_machines = len(machines)
    print('Read %d PMs from input:' % total_machines)
    for p in machines:
        print('  ' + str(p))
    print()

    # Initial run uses all available resources and does not tighten the constraints.
    switch_cpu_shares = []
    vhost_cpu_shares = []
    imbalance_vec = (1.0 + constants.SWITCH_CAPACITY_IMBALANCE_FACTOR, 1.0 + constants.VHOST_CPU_IMBALANCE_FACTOR)
    for pm in machines:
        switch_cpu_share = max(constants.INIT_SWITCH_CPU_SHARES, pm.min_switch_cpu_share)
        vhost_cpu_share = pm.max_cpu_share - switch_cpu_share
        switch_cpu_shares.append(switch_cpu_share)
        vhost_cpu_shares.append(vhost_cpu_share)

    # A task is a tuple (prev_edge_cut, prev_assignment, machines_used, machines_unused, switch_cpu_shares, vhost_cpu_shares)
    task_queue = [(total_vertex_weight, None, machines.copy(), [], switch_cpu_shares, vhost_cpu_shares)]
    assignment_hist = []
    assignment_signatures = []  # Should use a hash table or something.

    while len(task_queue) > 0:

        print('*' * 80)
        print(('  Assignment %d  ' % len(assignment_hist)).center(80, '*'))
        print('*' * 80)
        print()

        prev_edge_cut, prev_assignment, machines_used, machines_unused, switch_cpu_shares, vhost_cpu_shares = task_queue.pop(0)
        switch_cap_shares = [pm.capacity_func.eval(switch_cpu_shares[i]) for i, pm in enumerate(machines_used)]
        norm_switch_cap_shares = normalize_shares(switch_cap_shares)
        norm_vhost_cpu_shares = normalize_shares(vhost_cpu_shares)
        print('sw_cpu_shares: ' + str(switch_cpu_shares))
        print('sw_cap_shares: ' + str(switch_cap_shares))
        print('vh_cpu_shares: ' + str(vhost_cpu_shares))

        min_cut, assignment = metis.part_graph(metis_graph,
                                               nparts=len(machines_used),
                                               tpwgts=list(zip(norm_switch_cap_shares, norm_vhost_cpu_shares)),
                                               ubvec=imbalance_vec,
                                               recursive=False)
                                               # dbglvl=metis.mdbglvl_et.METIS_DBG_ALL)

        print('min_cut:       ' + str(min_cut))
        # print(assignment)
        print()

        switch_cap_usage = calculate_set_weights(graph, constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY, assignment)
        vhost_cpu_usage = calculate_set_weights(graph, constants.NODE_CPU_WEIGHT_KEY, assignment)
        used_cpu_shares = []
        unused_cpu_shares = []
        pm_weights = []

        for i, pm in enumerate(machines_used):
            # Find the exact CPU share needed to provide the allocated switch capacity.
            # TODO: Change this to binary search.
            actual_switch_cpu_share_needed = switch_cpu_shares[i]
            while pm.capacity_func.eval(actual_switch_cpu_share_needed) > switch_cap_usage[i]:
                actual_switch_cpu_share_needed -= 1
            while pm.capacity_func.eval(actual_switch_cpu_share_needed) < switch_cap_usage[i]:
                actual_switch_cpu_share_needed += 1
            actual_switch_cpu_share_needed = max(actual_switch_cpu_share_needed, pm.min_switch_cpu_share)
            pm_used_cpu_share = actual_switch_cpu_share_needed + vhost_cpu_usage[i]
            pm_unused_cpu_share = pm.max_cpu_share - pm_used_cpu_share
            used_cpu_shares.append(pm_used_cpu_share)
            unused_cpu_shares.append(pm_unused_cpu_share)

            # A heuristic index that measures how much workload this PM takes from the entire workload.
            pm_switch_weight = switch_cap_usage[i] / total_vertex_weight
            pm_vhost_weight = vhost_cpu_usage[i] / total_vhost_cpu_weight
            pm_weight = pm_switch_weight + pm_vhost_weight
            pm_weights.append(pm_weight)

            print(emphasize_used_pm(pm))
            print('  Switch:  CPU=%d, capacity=%.4lf, capacity_used=%.4lf, CPU_needed=%d' % (switch_cpu_shares[i], switch_cap_shares[i], switch_cap_usage[i], actual_switch_cpu_share_needed))
            print('  VHosts:  CPU=%d, CPU_used=%d' % (vhost_cpu_shares[i], vhost_cpu_usage[i]))
            print('  Overall: CPU_used=%d, CPU_unused=%d' % (pm_used_cpu_share, pm_unused_cpu_share))
            print('  Weights: sw_weight=%.4lf, vh_weight=%.4lf, total_weight=%.4lf' % (pm_switch_weight, pm_vhost_weight, pm_weight))
        print()

        # After excluding any PM, PM ID and array index will no longer match. We need to convert that in assignment.
        pm_index_mapping = [pm.pm_id for pm in machines_used]
        for i, a in enumerate(assignment):
            assignment[i] = pm_index_mapping[a]

        assignment_record = AssignmentRecord(assignment_id=len(assignment_hist), min_cut=min_cut,
                                             machines_used=machines_used, machines_unused=machines_unused,
                                             switch_cpu_shares=switch_cpu_shares, vhost_cpu_shares=vhost_cpu_shares,
                                             used_cpu_shares=used_cpu_shares, vhost_cpu_usage=vhost_cpu_usage,
                                             assignment=assignment)
        assignment_hist.append(assignment_record)
        assignment_signatures.append((machines_unused, switch_cpu_shares, vhost_cpu_shares))

        # To preserve state we copy the input lists.
        machines_used = machines_used.copy()
        machines_unused = machines_unused.copy()
        switch_cpu_shares = switch_cpu_shares.copy()
        vhost_cpu_shares = vhost_cpu_shares.copy()
        used_cpu_shares = used_cpu_shares.copy()
        unused_cpu_shares = unused_cpu_shares.copy()
        vhost_cpu_usage = vhost_cpu_usage.copy()

        # Test if we can get rid of the least used PM. We are very conservative here.
        least_used_pm_id = pm_weights.index(min(pm_weights))
        if sum(unused_cpu_shares) - unused_cpu_shares[least_used_pm_id] - used_cpu_shares[least_used_pm_id] > 0:
            # The unused CPU share of other PMs can cover this PM.
            # Here we assumed that other PMs can produce no less switch capacity with the CPU share used by this PM.
            machine_to_pop = machines_used.pop(least_used_pm_id)
            machines_unused.append(machine_to_pop)
            switch_cpu_shares.pop(least_used_pm_id)
            vhost_cpu_shares.pop(least_used_pm_id)
            used_cpu_shares.pop(least_used_pm_id)
            unused_cpu_shares.pop(least_used_pm_id)
            vhost_cpu_usage.pop(least_used_pm_id)
            print('PM #%d will be excluded from next round.' % machine_to_pop.pm_id)
            # We tried to add a new task here. It greatly increased search space but didn't improve result.
        else:
            # We can de-optimize this poor PM so that its contents go to other PMs.
            print('No PM can be excluded from next round.')
        print()
        # We could add a task here actually.

        # Tune parameters for next round.
        shares_changed = False
        for i, pm in enumerate(machines_used):
            print(emphasize_used_pm(pm))
            old_switch_cpu_share = switch_cpu_shares[i]
            old_vhost_cpu_share = vhost_cpu_shares[i]
            # For switch CPU share value, we move it towards the actual value needed. This adjustment will produce
            # nothing different in terms of assignment.
            actual_switch_cpu_share_needed = used_cpu_shares[i] - vhost_cpu_usage[i]
            next_switch_cpu_share = int(constants.SWITCH_CPU_SHARE_UPDATE_FACTOR * old_switch_cpu_share + (1 - constants.SWITCH_CPU_SHARE_UPDATE_FACTOR) * actual_switch_cpu_share_needed)
            if next_switch_cpu_share < pm.min_switch_cpu_share:
                next_switch_cpu_share = pm.min_switch_cpu_share
            elif next_switch_cpu_share > pm.max_switch_cpu_share:
                next_switch_cpu_share = pm.max_switch_cpu_share
            # We may update vhost CPU share later.
            next_vhost_cpu_share = vhost_cpu_usage[i]
            # Then we examine how much power is left on this PM.
            pm_unused_cpu_share = pm.max_cpu_share - next_switch_cpu_share - vhost_cpu_usage[i]
            pm_unused_ratio = pm_unused_cpu_share / pm.max_cpu_share
            print('  This round: switch_cpu=%d/%d, vhost_cpu=%d/%d, ratio=%.4lf' % (actual_switch_cpu_share_needed, old_switch_cpu_share, vhost_cpu_usage[i], old_vhost_cpu_share, pm_unused_ratio))
            if pm_unused_ratio > constants.PM_UNDER_UTILIZED_THRESHOLD:
                pm_free_cpu_share = int(pm_unused_cpu_share * (1 - constants.PM_UNDER_UTILIZED_PORTION_RESERVE_RATIO))
                pm_extra_switch_cpu_share = max(1, int(pm_free_cpu_share * actual_switch_cpu_share_needed / (actual_switch_cpu_share_needed + old_vhost_cpu_share)))
                if next_switch_cpu_share == pm.max_switch_cpu_share:
                    pm_extra_switch_cpu_share = 0
                pm_extra_vhost_cpu_share = pm_free_cpu_share - pm_extra_switch_cpu_share
                next_switch_cpu_share += pm_extra_switch_cpu_share
                next_vhost_cpu_share += pm_extra_vhost_cpu_share
                if next_vhost_cpu_share < old_vhost_cpu_share:
                    next_vhost_cpu_share = min(old_vhost_cpu_share, pm.max_cpu_share - next_switch_cpu_share)
                    print('  Under-utilized. sw_cpu+%d, vhost_cpu=%d' % (pm_extra_switch_cpu_share, next_vhost_cpu_share))
                else:
                    print('  Under-utilized. sw_cpu+%d, vhost_cpu+%d' % (pm_extra_switch_cpu_share, next_vhost_cpu_share - old_vhost_cpu_share))
            elif pm_unused_ratio < -1 * constants.PM_OVER_UTILIZED_THRESHOLD:
                # If the PM is under-utilized, the ratio is negative.
                # TODO: Think of better algorithm for this branch. For now I just cap the value.
                max_vhost_cpu_share = (pm.max_cpu_share - next_switch_cpu_share) * (1 + constants.PM_OVER_UTILIZED_THRESHOLD)
                # max_vhost_cpu_share = pm.max_cpu_share * (1 + constants.PM_OVER_UTILIZED_THRESHOLD) - next_switch_cpu_share
                print('  Over-utilized. vhost_cpu-%d' % (next_vhost_cpu_share - max_vhost_cpu_share))
                next_vhost_cpu_share = max_vhost_cpu_share
            # Update the array.
            if next_vhost_cpu_share != old_vhost_cpu_share or next_switch_cpu_share != old_switch_cpu_share:
                shares_changed = True
            switch_cpu_shares[i] = next_switch_cpu_share
            vhost_cpu_shares[i] = next_vhost_cpu_share
            print('  Next round: switch_cpu=%d, switch_cap=%.4lf, vhost_cpu=%d' % (next_switch_cpu_share, pm.capacity_func.eval(next_switch_cpu_share), next_vhost_cpu_share))

        # Try another round if any of the following conditions are met:
        if (
                # This is the first round.
                prev_assignment is None or
                # This round reduces edge cut (usually a sign of better partition). Maybe we can improve in next round.
                min_cut < prev_edge_cut or
                # Will use less machines next round.
                len(assignment_record.machines_used) > len(machines_used) or
                # Attempt a new share combination.
                shares_changed and (machines_unused, switch_cpu_shares, vhost_cpu_shares) not in assignment_signatures
        ):
            task_queue.append((min_cut, assignment_record, machines_used, machines_unused, switch_cpu_shares, vhost_cpu_shares))
        print()

    for a in assignment_hist:
        print(a)
        print()

    print('Best assignment is...')
    print()
    best_assignment = sorted(assignment_hist, key=AssignmentRecord.cmp_key)[0]
    print(best_assignment)


if __name__ == '__main__':
    main()

#!/usr/bin/python3

import argparse
import math
import operator
import functools
import sys
import inform
import networkx as nx
import matplotlib.pyplot as plt

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
    shares = [v if v > 0 else 1 for v in shares]
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


def visualize_assignment(graph, assignment, outfile_path=None, show=False):
    try:
        edge_weights = [math.log(w) / 2.4 for (u, v, w) in graph.edges(data='weight')]
    except:
        edge_weights = 1

    try:
        weights = [n[1][constants.NODE_SWITCH_CAPACITY_WEIGHT_KEY] for n in graph.nodes(data=True)]
        sizes = [math.pow(w, 0.55) * 6 for w in weights]
    except KeyError:
        weights = 50
        sizes = weights

    fig = plt.figure()
    # plt.title("Visualization of \"%s\"" % args.path, {'fontweight': 'bold'})
    plt.axis('off')
    pos = nx.nx_agraph.graphviz_layout(graph)

    nx.draw_networkx_nodes(graph, pos, node_size=sizes, node_color=assignment, cmap=plt.get_cmap('plasma'), alpha=0.95)
    nx.draw_networkx_edges(graph, pos, width=edge_weights, alpha=0.7)

    # nx.draw(graph, pos, with_labels=False, node_color=degrees, node_size=weights, cmap=plt.get_cmap('viridis'))
    fig.tight_layout()
    if outfile_path is not None:
        for fmt in ('svg', 'pdf'):
            plt.savefig(outfile_path + '.' + fmt, transparent=True, bbox_inches='tight', format=fmt, pad_inches=-0.4)
    if show:
        plt.show()
    plt.close()


def calc_switch_cpu_usage(pm, switch_cap_usage, switch_cpu_share=None):
    if switch_cpu_share is None:
        actual_switch_cpu_share_needed = pm.max_switch_cpu_share
    else:
        actual_switch_cpu_share_needed = switch_cpu_share
    while pm.capacity_func.eval(actual_switch_cpu_share_needed) > switch_cap_usage:
        actual_switch_cpu_share_needed -= 1
    while pm.capacity_func.eval(actual_switch_cpu_share_needed) < switch_cap_usage:
        actual_switch_cpu_share_needed += 1
    return max(actual_switch_cpu_share_needed, pm.min_switch_cpu_share)


class AssignmentRecord:

    def __init__(self, assignment_id, min_cut, machines_used, machines_unused,
                 switch_cpu_shares, vhost_cpu_shares, used_cpu_shares, vhost_cpu_usage, assignment):
        self.assignment_id = assignment_id
        self.min_cut = min_cut
        self.machines_used = machines_used
        self.machines_unused = machines_unused
        self.switch_cpu_shares = switch_cpu_shares
        self.vhost_cpu_shares = vhost_cpu_shares
        self.used_cpu_shares = used_cpu_shares
        self.vhost_cpu_usage = vhost_cpu_usage
        self.assignment = assignment
        self.overused_pms = 0
        self.underused_pms = 0

    def __repr__(self):
        s = underline('Assignment ' + str(self.assignment_id) + '\n')
        s += '  Min cut: %d\n' % self.min_cut
        s += '  Machines used:\n'
        for i, pm in enumerate(self.machines_used):
            if self.used_cpu_shares[i] > pm.max_cpu_share * (1 + constants.PM_OVER_UTILIZED_THRESHOLD):
                f = emphasize_overused_pm
                self.overused_pms += 1
            elif self.used_cpu_shares[i] < pm.max_cpu_share * (1 - constants.PM_UNDER_UTILIZED_THRESHOLD):
                f = emphasize_underused_pm
                self.underused_pms += 1
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


class MachineUsageResult:

    def __init__(self, old_index, pm, switch_cpu_share, vhost_cpu_share, switch_cap_usage, vhost_cpu_usage,
                 total_vertex_weight, total_cpu_weight):
        """
        Instantiate an object that synthesizes the usage info about a PM given an assignment.
        :param int old_index: The index of the PM before sorting.
        :param pm_model.Machine pm: The PM object.
        :param int switch_cpu_share: Input of CPU shares for switch part to get the assignment.
        :param int vhost_cpu_share: Input of CPU shares for vhost part to get the assignment.
        :param int switch_cap_usage: Actual amount of capacity assigned to the PM. Used for calculating sw CPU usage.
        :param int vhost_cpu_usage: Actual amount of CPU shares used by vhosts assigned to the PM.
        :param int total_vertex_weight: Sum of vertex weight (total capacity). Used for calculating weight.
        :param int total_cpu_weight: Sum of CPU weight of nodes. Used for calculating weight.
        """
        self.old_index = old_index
        self.pm = pm
        self.prev_switch_cpu_share = switch_cpu_share
        self.prev_vhost_cpu_share = vhost_cpu_share
        self.switch_cap_usage = switch_cap_usage
        self.vhost_cpu_usage = vhost_cpu_usage
        self.total_vertex_weight = total_vertex_weight
        self.total_cpu_weight = total_cpu_weight
        # Could have used binary search here.
        # actual_switch_cpu_share_needed = switch_cpu_share
        # while pm.capacity_func.eval(actual_switch_cpu_share_needed) > switch_cap_usage:
        #     actual_switch_cpu_share_needed -= 1
        # while pm.capacity_func.eval(actual_switch_cpu_share_needed) < switch_cap_usage:
        #     actual_switch_cpu_share_needed += 1
        self.switch_cpu_usage = calc_switch_cpu_usage(pm, switch_cap_usage, switch_cpu_share)

    @property
    def cpu_share_used(self):
        return self.switch_cpu_usage + self.vhost_cpu_usage

    @property
    def cpu_share_free(self):
        return self.pm.max_cpu_share - self.cpu_share_used

    @property
    def switch_share_weight(self):
        return self.switch_cap_usage / self.total_vertex_weight

    @property
    def vhost_share_weight(self):
        return self.vhost_cpu_usage / self.total_cpu_weight

    @property
    def total_weight(self):
        return self.switch_share_weight + self.vhost_share_weight

    def is_over_utilized(self, delta=0):
        return self.cpu_share_used + delta > int(self.pm.max_cpu_share * (1 + constants.PM_OVER_UTILIZED_THRESHOLD))

    def over_utilized_shares(self, delta=0):
        return self.cpu_share_used + delta - self.pm.max_cpu_share

    def is_under_utilized(self, delta=0):
        return int(self.pm.max_cpu_share * (1 - constants.PM_UNDER_UTILIZED_THRESHOLD)) > (self.cpu_share_used + delta)

    def under_utilized_shares(self, delta=0):
        return int(self.pm.max_cpu_share * (1 - constants.PM_UNDER_UTILIZED_THRESHOLD)) - (self.cpu_share_used + delta)

    @property
    def emphasis_color(self, delta=0):
        if self.is_over_utilized(delta):
            return emphasize_overused_pm
        elif self.is_under_utilized(delta):
            return emphasize_underused_pm
        else:
            return emphasize_used_pm

    def print(self):
        print(str(self.old_index) + ': ' + str(self.emphasis_color(self.pm)))
        print('  Switch Used/Alloc:  CPU = %d / %d, Cap = %.4lf / %.4lf' % (
            self.switch_cpu_usage, self.prev_switch_cpu_share,
            self.switch_cap_usage, self.pm.capacity_func.eval(self.prev_switch_cpu_share)))
        print('  Vhost  Used/Alloc:  CPU = %d / %d' % (self.vhost_cpu_usage, self.prev_vhost_cpu_share))
        print('  Overall: CPU = %d / %d' % (self.cpu_share_used, self.pm.max_cpu_share))
        print('  Weights: sw = %.4lf, vcpu = %.4lf, total = %.4lf' % (
            self.switch_share_weight, self.vhost_share_weight, self.total_weight))


def main():
    parser = argparse.ArgumentParser(description='A refined graph partition algorithm based on METIS.')
    parser.add_argument('-g', '--graph-file', type=str, required=True, help='File to read input graph from.')
    parser.add_argument('-p', '--pm-file', type=str, required=True, help='File to read PM information.')
    parser.add_argument('-c', '--vhost-cpu-file', type=str, required=True, help='File to read vhost CPU information.')
    parser.add_argument('-o', '--out', type=str, required=False, default=None, help='If given, will generate output files to this dir.')
    args = parser.parse_args()

    print(args)
    print()

    # Print the constant params.
    print('Program parameters:')
    for k in constants.__all__:
        print('  %s: %s' % (k, getattr(constants, k)))
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
        # If this scheme should be changed, update the PM bring-back logic as well.
        switch_cpu_share = max(constants.INIT_SWITCH_CPU_SHARES, pm.min_switch_cpu_share)
        vhost_cpu_share = pm.max_cpu_share - switch_cpu_share
        switch_cpu_shares.append(switch_cpu_share)
        vhost_cpu_shares.append(vhost_cpu_share)

    # A task is a tuple of
    # (prev_edge_cut, prev_assignment, machines_used, machines_unused, switch_cpu_shares, vhost_cpu_shares)
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

        if len(machines_used) == 1:
            min_cut = 0
            assignment = [0] * graph.number_of_nodes()
        else:
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
        machine_usages = []

        # Associate information about usage of a single PM to an object.
        for i, pm in enumerate(machines_used):
            machine_usage = MachineUsageResult(old_index=i, pm=pm,
                                               switch_cpu_share=switch_cpu_shares[i], vhost_cpu_share=vhost_cpu_shares[i],
                                               switch_cap_usage=switch_cap_usage[i],
                                               vhost_cpu_usage=vhost_cpu_usage[i],
                                               total_vertex_weight=total_vertex_weight,
                                               total_cpu_weight=total_vhost_cpu_weight)
            # machine_usage.print()
            machine_usages.append(machine_usage)
        # print()

        # After excluding any PM, PM ID and array index will no longer match. We need to convert that in assignment.
        pm_index_mapping = [pm.pm_id for pm in machines_used]
        for i, a in enumerate(assignment):
            assignment[i] = pm_index_mapping[a]

        assignment_record = AssignmentRecord(assignment_id=len(assignment_hist), min_cut=min_cut,
                                             machines_used=machines_used, machines_unused=machines_unused,
                                             switch_cpu_shares=switch_cpu_shares, vhost_cpu_shares=vhost_cpu_shares,
                                             used_cpu_shares=[u.cpu_share_used for u in machine_usages],
                                             vhost_cpu_usage=vhost_cpu_usage,
                                             assignment=assignment)
        assignment_hist.append(assignment_record)
        assignment_signatures.append((machines_unused, switch_cpu_shares, vhost_cpu_shares))

        # To preserve state we copy the input lists.
        machines_used = machines_used.copy()
        machines_unused = machines_unused.copy()
        switch_cpu_shares = switch_cpu_shares.copy()
        vhost_cpu_shares = vhost_cpu_shares.copy()

        # Sort the PMs by descending total weight.
        machine_usages.sort(key=lambda u : -u.total_weight)

        # Check if the least used PM can be eliminated. If the free CPU shares of all other PMs can cover the
        # CPU shares undertaken by this PM, then this PM can be removed from list.
        # It doesn't matter doing this either before or after adjustment because the decision won't change.
        least_used_pm = machine_usages[-1]
        total_cpu_shares_free = sum([u.cpu_share_free for u in machine_usages]) - least_used_pm.cpu_share_free
        print('PM Elimination Phase:')
        print('  Target PM: #%d, sticky=%s' % (least_used_pm.pm.pm_id, str(least_used_pm.pm.sticky)))
        print('  Total free CPU shares: %d' % total_cpu_shares_free)
        print('  Shares covered by PM:  %d' % least_used_pm.cpu_share_used)
        if total_cpu_shares_free - least_used_pm.cpu_share_used > 0 and not least_used_pm.pm.sticky:
            # The unused CPU share of other PMs can cover this PM.
            # This is conservative because in general other PMs can produce no less switch capacity with the CPU
            # hare used by this PM.
            machines_used.pop(least_used_pm.old_index)
            machines_unused.append(least_used_pm.pm)
            switch_cpu_shares.pop(least_used_pm.old_index)
            vhost_cpu_shares.pop(least_used_pm.old_index)
            print('  PM #%d will be excluded from next round.' % least_used_pm.pm.pm_id)
            task_queue.append(
                (total_vertex_weight, None, machines_used, machines_unused, switch_cpu_shares, vhost_cpu_shares))
            print()
            continue
            # We tried to add a new task here. It greatly increased search space but didn't improve result.
        else:
            # We can de-optimize this poor PM so that its contents go to other PMs.
            print('  No PM can be excluded from next round.')
        print()

        # From the PM that takes the most weight to the PM that takes the least weight, check if it's over-utilized,
        # just fine, or under-utilized.
        num_overloaded_pms = 0
        prev_pm_under_utilized = False
        vhost_cpu_deltas = [0] * len(machine_usages)
        switch_cpu_deltas = [0] * len(machine_usages)
        print('Share Adjustment Phase:')
        for i, pm in enumerate(machine_usages):
            total_delta = vhost_cpu_deltas[i] + switch_cpu_deltas[i]
            pm.print()
            if pm.is_over_utilized(total_delta):
                num_overloaded_pms += 1
                shares_over = pm.over_utilized_shares(total_delta)
                shares_to_discard = shares_over # int(shares_over * (1 - constants.PM_OVER_UTILIZED_PORTION_RESERVE_RATIO))
                if i < len(machine_usages) - 1:
                    pm_next = machine_usages[i + 1]
                    curr_pm_switch_delta = int(shares_to_discard * pm.switch_cpu_usage / pm.cpu_share_used)
                    if pm.switch_cpu_usage + switch_cpu_deltas[i] - curr_pm_switch_delta < pm.pm.min_switch_cpu_share:
                        curr_pm_switch_delta = pm.switch_cpu_usage + switch_cpu_deltas[i] - pm.pm.min_switch_cpu_share
                    switch_cpu_deltas[i] -= curr_pm_switch_delta
                    vhost_cpu_deltas[i] -= shares_to_discard - curr_pm_switch_delta
                    switch_cpu_deltas[i +  1] += int(shares_to_discard * pm_next.switch_cpu_usage / (pm_next.switch_cpu_usage + pm_next.vhost_cpu_usage))
                    vhost_cpu_deltas[i + 1] += shares_to_discard - switch_cpu_deltas[i +  1]
                    print('  Over by %d shares. Dispose %d shares to the next PM.' % (shares_over, shares_to_discard))
                else:
                    if pm.switch_cpu_usage + switch_cpu_deltas[i] > pm.pm.max_switch_cpu_share:
                        switch_cpu_deltas[i] = pm.pm.max_switch_cpu_share - pm.switch_cpu_usage
                    if switch_cpu_deltas[i] + vhost_cpu_deltas[i] + pm.cpu_share_used > pm.pm.max_cpu_share:
                        vhost_cpu_deltas[i] = pm.pm.max_cpu_share - pm.switch_cpu_usage - switch_cpu_deltas[i] - pm.vhost_cpu_usage
                    print('  Over by %d shares. No other PM can take it.' % (shares_over))
                prev_pm_under_utilized = False
            elif pm.is_under_utilized(total_delta):
                shares_under = pm.under_utilized_shares(total_delta)
                shares_usable = max(1, int(shares_under * (1 - constants.PM_UNDER_UTILIZED_PORTION_RESERVE_RATIO)))
                if i > 0 and prev_pm_under_utilized and shares_usable > vhost_cpu_deltas[i - 1]:
                    shares_usable = vhost_cpu_deltas[i - 1]
                print('  Under-utilized shares: %d. Adjustable shares: %d.' % (shares_under, shares_usable))
                switch_cpu_delta = max(1, int(shares_usable * pm.switch_cpu_usage / pm.cpu_share_used))
                if pm.switch_cpu_usage + switch_cpu_delta > pm.pm.max_switch_cpu_share:
                    switch_cpu_delta = pm.pm.max_switch_cpu_share - pm.switch_cpu_usage
                vhost_cpu_delta = shares_usable - switch_cpu_delta
                if vhost_cpu_delta < 0:
                    vhost_cpu_delta = 0
                switch_cpu_deltas[i] += switch_cpu_delta
                vhost_cpu_deltas[i] += vhost_cpu_delta
                prev_pm_under_utilized = True
            else:
                print('  Share in reasonable range.')
                prev_pm_under_utilized = False
            print('  Switch deltas: ' + str(switch_cpu_deltas))
            print('  Vhost deltas:  ' + str(vhost_cpu_deltas))
        print()
        for i, pm in enumerate(machine_usages):
            pm.switch_cpu_delta = switch_cpu_deltas[i]
            pm.vhost_cpu_delta = vhost_cpu_deltas[i]

        # Change the order back to index-based.
        machine_usages.sort(key=lambda u: u.old_index)

        # Extract the input for next round.
        switch_cpu_shares_new = []
        vhost_cpu_shares_new = []
        for pm in machine_usages:
            # Note that our next input is based on current output. Given a graph shape and some preliminary resource
            # quantification, there isn't much to tune.
            next_switch_cpu_share = pm.switch_cpu_usage + pm.switch_cpu_delta
            # if next_switch_cpu_share > pm.pm.max_switch_cpu_share:
            #     next_switch_cpu_share = pm.pm.max_switch_cpu_share
            # elif next_switch_cpu_share < pm.pm.min_switch_cpu_share:
            #     next_switch_cpu_share = pm.pm.min_switch_cpu_share
            switch_cpu_shares_new.append(next_switch_cpu_share)
            next_vhost_cpu_share = pm.vhost_cpu_usage + pm.vhost_cpu_delta
            if next_vhost_cpu_share + next_switch_cpu_share > pm.pm.max_cpu_share:
                next_vhost_cpu_share = pm.pm.max_cpu_share # Treat switch part as "overclocked" portion.
            vhost_cpu_shares_new.append(next_vhost_cpu_share)
        shares_changed = switch_cpu_shares_new != switch_cpu_shares or vhost_cpu_shares_new != vhost_cpu_shares
        switch_cpu_shares = switch_cpu_shares_new
        vhost_cpu_shares = vhost_cpu_shares_new

        # Try another round if any of the following conditions are met:
        if len(machines_used) > 0 and (
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

        if num_overloaded_pms == len(machines_used) and len(machines_unused) > 0:
            # All used PMs are overloaded but we have free machines.
            machines_used = machines_used.copy()
            machines_unused = machines_unused.copy()
            switch_cpu_shares = switch_cpu_shares.copy()
            vhost_cpu_shares = vhost_cpu_shares.copy()
            m = machines_unused.pop()   # The machine to bring back from free list.
            i = 0
            for pm in machines_used:
                if m.pm_id < pm.pm_id:
                    break
                i += 1
            machines_used.insert(i, m)
            switch_cpu_shares.insert(i, constants.INIT_SWITCH_CPU_SHARES)
            vhost_cpu_shares.insert(i, m.max_cpu_share - constants.INIT_SWITCH_CPU_SHARES)
            m.sticky = True
            task_queue.append(
                (min_cut, assignment_record, machines_used, machines_unused, switch_cpu_shares, vhost_cpu_shares))
            print('Brought PM #%d back to list.' % m.pm_id)

        print()

    for a in assignment_hist:
        print(a)
        if args.out is not None:
            outfile_prefix = args.out + '/assignment_' + str(a.assignment_id)
            with open(outfile_prefix + '.txt', 'w') as f:
                f.write('\n'.join([str(v) for v in a.assignment]) + '\n')
            # Graph files will be prefix + {.svg|.pdf}.
            visualize_assignment(graph, a.assignment, outfile_path=outfile_prefix)
        print()

    print('Best assignment out of %d candidates is...' % len(assignment_hist))
    print()
    best_assignment = sorted(assignment_hist, key=operator.attrgetter('overused_pms', 'min_cut'))[0]
    print(best_assignment)


if __name__ == '__main__':
    main()

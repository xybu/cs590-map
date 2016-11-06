We have been having trouble determining the value of K' (the min number of PMs needed) as input but determining K' is kind of critical. There are two directions:

1. Find a mathematically provable way of determining K' if used as input.
2. Try with some initial K' value, and use the output as feedback to determine what a better K' could be (feedback heuristic).

## Problem Formulation

The question is something like this: given the capacity and CPU shares of PMs, we want to find a smallest subset of PMs that can accomodate the topology.

| PM       | PM #1 | PM #2 | ... | PM #k | Total Required              |
| -------- | ----- | ----- | --- | ----- | --------------------------- |
| Capacity | W1    | W2    | ... | Wk    | W = Sum of vertex weight.   |
| CPU      | C1    | C2    | ... | Ck    | C = Sum of vhost CPU share. |

What's the smallest subset of PMs `P = {PM #a, PM #b, ..}` and `k' = |P|` that can satisfy all three conditions below:

1. 1 <= `k'` <= `k`
2. Sum of W_x, x in P, >= W
3. Sum of C_x, x in P, >= C

How good can we solve this problem?
 * Can we determine the size of `P`, that is, `k'`?
 * Can we determine the elements of `P`?
 * If we can't, can we at least give a lower bound for the value of `k'`?

For example, given

| PM       | PM #1 | PM #2 | PM #3 | PM #4 | Total Required |
| -------- | ----- | ----- | ----- | ----- | -------------- |
| Capacity | 3536  | 1792  | 9127  | 14066 | 23080          |
| CPU      | 90    | 85    | 80    | 85    | 510            |

What's the min number of PMs that can satisfy the total required? What are they?


Some wild thoughts:
 * Also we should note that the two constraints are correlated. If there is excessive capacity
but insufficient CPU we may convert one to another.
 * A PM can be excluded if all its shares can be met by the unused portions of other PMs.
 * If there is only one machine, then we have no choice.
 * If there is no "surplus" on any constraint, all PMs must be chosen.
 * Any view from economics perspective?

## Ideas

Subset sum? Knapsack?

## Feedback Heuristic

Where to start (at least we have a tight lowerbound for `k'`)?

Rules for moving? If all PMs over-utilized and we have spare PM, add one more?

## Backup code

Move some dead code here just in case.

```python

def choose_machines(machines, switch_cpu_shares, vhost_cpu_shares, total_switch_cap_req, total_vhost_cpu_req):
    """
    Determine a subset of PMs to use given the switch and CPU requirements.
    :param list[pm_model.Machine] machines: All the available PMs.
    :param list[int] switch_cpu_shares: CPU share for switch on each PM. Use cap function to convert to switch power.
    :param list[int] vhost_cpu_shares: CPU share for vhosts on each PM.
    :param int total_switch_cap_req: Total amount of switch power needed.
    :param int total_vhost_cpu_req: Total amount of vhost CPU needed.
    :return list[pm_model.Machine]: A list of PMs chosen.
    """
    total_machines = len(machines)
    assert(total_machines == len(switch_cpu_shares))
    assert(total_machines == len(vhost_cpu_shares))
    if total_machines == 1:
        # If there is only one machine, then we have no choice.
        return machines
    switch_cap_shares = [machines[i].capacity_func.eval(v) for i, v in enumerate(switch_cpu_shares)]
    sum_switch_cap_shares = sum(switch_cap_shares)
    sum_vhost_cpu_shares = sum(vhost_cpu_shares)
    if sum_switch_cap_shares <= total_switch_cap_req or sum_vhost_cpu_shares <= total_vhost_cpu_req:
        # If there is no "surplus" on any constraint, all PMs must be chosen.
        return machines
    # Here both constraints have surplus.
    # We focus on the one that has tighter bound (less surplus) and see
    # if we can reduce one PM from the list.
    switch_cap_surplus_ratio = sum_switch_cap_shares / total_switch_cap_req
    vhost_cpu_surplus_ratio = sum_vhost_cpu_shares / total_vhost_cpu_req
    if vhost_cpu_surplus_ratio < switch_cap_surplus_ratio:
        # Here vhost CPU resource is scarcer thus more valuable.
        # We scan through all PMs to explore all possibilities.
        # In the past we focus on the min one.
        pm_potential_victims = []
        for i in range(total_machines):
            if sum_vhost_cpu_shares - vhost_cpu_shares[i] >= sum_vhost_cpu_shares:
                pm_potential_victims.append(i)

        min_vhost_cpu_share = min(vhost_cpu_shares)
        if sum_vhost_cpu_shares - min_vhost_cpu_share < sum_vhost_cpu_shares:
            # If getting rid of the PM that provides the least vhost CPU share
            # will make vhost CPU insufficient, we cannot get rid of it.
            return machines
        else:
            # Removing the PM that provides the least vhost CPU share doesn't
            # invalidate vhost CPU constraint. Let's check if switch capacity
            # constraint is preserved.
            pm_id_to_exclude = vhost_cpu_shares.index(min_vhost_cpu_share)
            remaining_sum_switch_cap_shares = sum_switch_cap_shares
```

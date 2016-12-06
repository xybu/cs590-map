## Overview

Our program converts a graph and list of physical machines (PMs) along with the resource requirements
to input used by METIS (a single-objective, multi-constraint graph partitioner), and given some output
from METIS, tunes the requirements and searches for better partition results.

## Input Format

### Graph Input

We follow input format defined by Chaco (because of laziness).

### Node CPU Requirement

A text file with `N` lines, where `N` equals the number of vertices in the graph. The first line is CPU required for vertex 1, and second line for vertex 2, ....

### Physical Machines (PMs)

Input for physical machine is a text file with `N` lines, where `N` is the
number of PMs. Each line specifies a PM in the following format:

```
MAX_CPU_SHARE MIN_SWITCH_CPU_SHARE MAX_SWITCH_CPU_SHARE c_0 c_1 c_2 ...
```

where
 * `MAX_CPU_SHARE`: the maximum CPU shares (usually 100xNCores; use a smaller value to represent system overhead).
 * `MIN_SWITCH_CPU_SHARE`: Use no less than this amount of CPU share to packet processing on the PM.
 * `MAX_SWITCH_CPU_SHARE`: Use no more than this amount of CPU share to packet processing on the PM.
 * `0` <= `MIN_SWITCH_CPU_SHARE` <= `MAX_SWITCH_CPU_SHARE` <= `MAX_CPU_SHARE`.
 * `c_0` ... `c_m` are the coefficients for the capacity function. `f(u) = c_0 + c_1 * u + c_2 * u^2 + ...`. We require that the function cannot always evaluate to 0.

The numbers can be separated by spaces or tabs. Empty lines or lines starting with `#` will be ignored.

## Algorithm

### About Memory Requirement

Our model currently takes only CPU shares into consideration, but memory requirement can be easily added in the manner CPU requirement is fulfilled:

* Add memory limit as a new constraint to METIS.
* Specify memory requirement for each vertex by adding one more weight.
* Model the relation between memory usage and switching capacity.

### Data Structure

#### Graph Modelling

The topology is a graph `G=(V, E)`.

Each vhost / switch is a vertex with two weights -- cap weight and CPU weight.

Each link is an edge with one weight -- link bandwidth.

#### Capacity Function

Assuming capacity functions are polynomial, we abstract capacity function as a sequence of coefficients `a_n, a_(n-1), ..., a_0`.
Given a CPU share value `u` the capacity function returns the switching capacity that `u` shares of CPU can sustain `f(u) = a_n*u^n + a_(n-1)*u^(n-1) + ... + a_0`.

#### Physical Machine

For each PM we form an object with the following properties:

* `pm.pm_id`: A unique identifier of the PM.
* `pm.capacity_func`: Capacity function of the PM.
* `pm.MAX_CPU_SHARE`
* `pm.MIN_SWITCH_CPU_SHARE`
* `pm.MAX_SWITCH_CPU_SHARE`

A PM is "overloaded" (or "over-utilized") if ...

A PM is "under-utilized" if ...

### Parameters

The algorithm takes a set of parameters from user. Some adjusts the requirement tightness and some tunes the step size. Those values do not change after program is loaded. Some notable ones are:

 * Load imbalance tolerance for switch capacity constraint is ` constants.SWITCH_CAPACITY_IMBALANCE_FACTOR` (default: 0.1).
 * Load imbalance tolerance for vhost CPU constraint is `constants.VHOST_CPU_IMBALANCE_FACTOR` (default: 0.15).
 * Threshold for PM over-utilization (default: if CPU share needed to cover the load is 10% more than the max CPU share of this PM).
 * Threshold for PM under-utilization (default: if CPU share needed to cover the load is no more than 90% of max CPU share of this PM).

### Outer Loop

The program has an input queue to hold input that will be tried, and a hash set that saves the input along with its result (i.e., assignment and edge cut):

```python
// Starting point.
input_queue = [
  {
    'prev_assignment': None,
    'min_cut': total_vertex_weight,
    'pms_used': all_pms,
    'pms_excluded': [],
    'switch_cpu_shares': [constants.INIT_SWITCH_CPU_SHARES] * len(all_pms)
    'vhost_cpu_shares': [(all_pms[i].MAX_CPU_SHARE - constants.INIT_SWITCH_CPU_SHARES) for i from 0 to len(all_pms)]
  }]

// Can be done by parallel workers.
while (!input_queue.empty()) {
  perform_partition(**input_queue.dequeue())
}
print_the_best_partition()
```

The procedure `perform_partition()` takes the following input:

1. Result of parent iteration (assignment and edge cut)
2. Lists of chosen PMs (PMs that will be used in this round) and excluded PMs (PMs determined to be not needed from previous rounds).
3. CPU shares for switching and vhost, respectively, for each PM.

Initial input consists of the following values:

* No parent assignment, 
* All PMs are chosen and no PM is excluded.
* Each PM is allocated `constants.INIT_SWITCH_CPU_SHARES` (default: 20) or PM's 
  `MIN_SWITCH_CPU_SHARE`  percent CPU, whichever is greater, for packet processing.
* Rest of the CPU share is allocated to fulfill vhost CPU requirements.

### Single Step

The logic of `perform_partition()` is as follows:

 1. For every PM, calculate switch capacity value from capacity function and switch CPU share.
 2. Normalize vhost CPU shares and switch capacity (that is, x => x / sum) values.
 3. Call METIS k-way partition API and obtain the min cut and assignment result.
 4. Save the iteration result to hash set.
 5. For each PM, calculate the following values:
	 1. `sw_cap`: How much switch capacity is assigned to the PM (that is, sum of vertex weight).
	 2. `vhost_cpu_usage`: How much vhost CPU share is needed by the vertices assigned to the PM (that is, sum of vhost CPU requirements of all vertices).
	 3. `sw_cpu_usage`: How many switch CPU shares are needed to provide the assigned switch capacity. Note that this value can be either more or less than the switch CPU shares used in input. Note that if we change the input
        CPU share to this value with everything else the same the result will remain the same.
	 4. The weights carried by the PM:
		 * `wv` = `vhost_cpu_usage` / total_vhost_cpu and
		 * `ws` = `sw_cap` / total_switch_capacity
 6. Eliminate unneeded PMs (explained later). May add to input queue.
 7. Tune CPU shares (explained later). May add to input queue.

```python
// Calculate switch capacity for each PM.
switch_cap_values = []
for i from 0 to len(pms_used):
  sw_cpu_share = switch_cpu_shares[i]
  sw_cap_value = pms_used[i].capacity_func(sw_cpu_share)
  switch_cap_values.append(sw_cap_value)

// Normalize input for METIS. The actual normalization procedure is called "normalize_shares()" in main.py.
// For example, [90, 80, 70, 60] => [0.3, 0.267, 0.233, 0.2]
total_cap_values = sum(switch_cap_values)
switch_cap_frac = [v / total_cap_values for v in switch_cap_values]
total_cpu_shares = sum(vhost_cpu_shares)
vhost_cpu_frac = [v / total_cpu_shares for v in vhost_cpu_shares]

// Call METIS API.
min_cut, assignment = METIS(graph, nparts=len(pms_used), tpwgts=zip(switch_cap_frac, vhost_cpu_frac))

// Save the result to assignment history.
// Signature is (pms_excluded, switch_cpu_shares, vhost_cpu_shares).
add_to_assignment_hist(pms_used, pms_excluded, switch_cpu_shares, vhost_cpu_shares, min_cut, assignment)

sw_cap_usage = For each PM, sum of vertex weights of vertices assigned to the PM.
sw_cpu_usage = For each PM `i`, the min CPU share `u` such that `pm.capacity_func(u) >= sw_cap_usage[i]`.
vhost_cpu_usage = For each PM, sum of CPU shares needed by vertices assigned to the PM.

// Calculate the weights carried by each PM.
pm_weights = []
for i from 0 to len(pms_used):
  ws = sw_cap_usage[i] / total_switch_capacity // total_switch_capacity is sum of weights of all vertices.
  wv = vhost_cpu_usage[i] / total_vhost_cpu // total_vhost_cpu is sum of CPU weights of all vertices.
  pm_weights.append(ws+wv)

sort_pms_used_by_decreasing_pm_weights()

if (!eliminate_pms())
    tune_cpu_shares()
```

#### PM Elimination

The least used PM (i.e., the PM with smallest `wv+ws` value) is decided to be unnecessary if the unused CPU shares of all other PMs can cover the shares undertaken by this PM. For example, if the portion of graph on a PM uses a total of 40 CPU shares but all other PMs have 50 free CPU shares in total, then this PM can be excluded.

In PM Elimination phase we check if the PM taking smallest `wv+ws` can be eliminated. If so, move this PM from inclusion list to exclusion list, and add to input queue the adjusted input. Unneeded PMs are usually eliminated in the earliest rounds.

Here we rely on the fact that capacity function of PMs reflects to some extent their performance -- To provide equal amount of switch capacity, a weaker PM uses more CPU shares. In the previous example, if that (weakest) PM uses 40 CPU shares in total, then no other PM needs more than 40 CPU shares to handle the load, not to mention the load may be split onto other PMs.

To address a corner case in which all used PMs are overloaded yet there is at least one unused PM, the last removed (i.e., the strongest of the weaks) PM will be brought back and set sticky (thus won't be excluded once again).

```python
unused_shares = []
for i from 0 to len(pms_used):
  unused_shares.append(pms_used[i].MAX_CPU_SHARE - sw_cpu_usage[i] - vhost_cpu_usage[i])
least_used_pm = index of PM with the smallest wv+ws value.
if sum(unused_shares) - unused_shares[least_used_pm] > sw_cpu_usage[i] + vhost_cpu_usage[i]:
  exclude PM least_used_pm and add to queue the new input
```

#### CPU Share Tuning

In this phase we first sort the PMs by descending `wv+ws`, then calculate CPU shares for next round based on output of this round.

The high-level idea is that, if a PM is overloaded, move some of its shares to the next most powerful PM; if a PM is under-utilized, allocate more shares but no more than the shares added to any stronger under-utilized PM.

1. `vhost_cpu_deltas = [0] * len(machine_used)`
2. `switch_cpu_deltas = [0] * len(machine_used)`
3. For PM `i` from the one with highest `wv+ws` to the one with lowest `wv+ws` do:
	1. If the PM is over-utilized after adding `total_delta = vhost_cpu_deltas[i] + switch_cpu_deltas[i]` more shares AND there is a next PM:
		1. Calculate the over-utilized shares `shares_over = total_delta + vhost_cpu_usage + sw_cpu_usage - pm.MAX_CPU_SHARE`.
		2. Switch CPU share of this PM for next round will be `next_sw_share = min(max(adj_sw_share, pm.MIN_SWITCH_CPU_SHARE), pm.MAX_SWITCH_CPU_SHARE)` where `adj_sw_share = sw_cpu_usage + switch_cpu_deltas[i] - shares_over * (sw_cpu_usage / (vhost_cpu_usage + sw_cpu_usage))`. Basically we use the switch CPU usage as the base, then proportionally reduce the overused shares, and enforce the switch CPU share range.
		3. Vhost CPU share of this PM for next round will be `vhost_cpu_usage + shares_over - (next_sw_share - sw_cpu_usage)`.
		4. Distribute `shares_over` to `switch_cpu_deltas[i + 1]` and `vhost_cpu_deltas[i + 1]` proportionally to `sw_cpu_usage` and `vhost_cpu_usage` of the next PM.
	2. If the PM is under-utilized after taking `total_delta` shares:
		1. Calculate the under-utilized shares `shares_under = pm.MAX_CPU_SHARE * (1 - constants.PM_UNDER_UTILIZED_THRESHOLD)) - (vhost_cpu_usage + sw_cpu_usage + total_delta)`.
		2. Going to allocate `shares_usable = max(1, int(shares_under * (1 - constants.PM_UNDER_UTILIZED_PORTION_RESERVE_RATIO)))` more shares to this PM. That is, at least 1 share, at most the usable portion of `shares_under`.
		3. But if there is a previous PM and this PM is under-utilized, the `shares_usable` calculated in previous step is capped by `vhost_cpu_deltas[i - 1]` (so that the added share won't be more than any stronger PM).
		4. Switch CPU share of this PM for next round will be `next_sw_share = min(max(adj_sw_share, pm.MIN_SWITCH_CPU_SHARE), pm.MAX_SWITCH_CPU_SHARE)` where `adj_sw_share = sw_cpu_usage + switch_cpu_deltas[i] + shares_usable * (sw_cpu_usage / (vhost_cpu_usage + sw_cpu_usage))`. Basically we assign the free shares proportionally to current usage and enforce range limit.
		5. Vhost CPU share of this PM for next round will be `vhost_cpu_usage + shares_usable - (next_sw_share - sw_cpu_usage)`.
	3. If the PM is neither over-utilized nor under-utilized:
		1. `next_sw_share = sw_cpu_usage + switch_cpu_deltas[i]` and enforce range limit.
		2. `next_vhost_share = vhost_cpu_usage + vhost_cpu_deltas[i]`.

After the adjustment, the new input will be added to input queue if

1. It's the first iteration (parent assignment is NULL).
2. Edge cut is reduced in this round (we may do better by adjusting the params).
3. The input signature has not been tried before.

```python
```

#### Convergence

The program usually stops very fast because we are using the constraints as upperbounds instead of exact-fit requirements (that is, imbalance vector is set relatively leniently). Our tweaks result in relocations of boundary nodes and the partitions are very similar.

Another factor that helps the program to converge is that the CPU share adjustment moves CPU shares "like a waterfall" -- Overloaded shares flow towards next most powerful PMs, and the room left for expansion in an under-utilized PM is limited.

#### When Resource is Not Enough

The normalization step converts absolute values to fractions, which scales available resources up to meet the need.

### Best Assignment Determination

The program stops when input queue becomes empty. Then the program picks the best assignment. Currently the criteria is min edge cut. This works well in practice because

* Assignments with more PMs used tend to have larger edge cut values (because there are more sets).
* Even if the assignment overloads some PM, the degree is usually acceptable and adjustable (by using conservative over-utilization threshold).

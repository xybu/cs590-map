There are a few ways to reduce the gap between prev input and next input:

1. Set imb vec to [0.01, 0.01] of subsequent shares of each branch in share adjustment phase -- METIS gives bad result.
2. Use a moving average for prev and next (derived) input -- adopted by this version.
3. Derive next input from prev input, rather than basing next input on result of prev input -- v5.

The branching strategy of v4 is to including more PMs as needed, instead of
eliminating PMs.

## Calculating the minimum set of PMs needed

This step is to find out the smallest set of PMs needed so that branching step only extends the set. To obtain the
smallest possible (lowerbound) set, for each resource we estimate scarcity by max possible available and min
possible need.

For CPU share resource the max possible each PM can offer is its MAX_CPU_SHARE value. The minimum possible need is
the sum of vhost CPU requirements. Actual need is at least this value because of need for packet switching.

For switching capacity resource the max possible each PM can offer is the capacity at the PM's MAX_SWITCH_CPU_SHARE.
The minimum possible and actual need is the sum of vertex weights in the graph.

If more constraints are to added, the same logic applies.

The problem is stated as follows:

```
Objective:
    Min number of PMs chosen

Constraints:
    For each resource R_i,
        sum(max possible offering for R_i by each PM) >= min need for R_i
```

A greedy approach based on assumption that need for one particular resource usually dominates need for all other
resources.

1. Sort the resource constraints from most to least scarce (i.e., in ascending order of sum of max available from each PM / min_need).
   Let the sorted resource constraints be Ra, Rb, ..., Rs.

2. Use each PM's max possible offerings for each of resources Ra, Rb, ..., Rs, as keys and sort the PMs in descending order.
   Let the sorted PM list be PM1, PM2, ..., PMk.

3. Starting from empty set {}, iteratively put PM1, PM2, ..., PMk' to the set until for all resources the max possible
   offering for the resource by all PMs in the set is at least the min possible need for that resource. 

## Evaulation

When resource is aboundant, the program runs significantly faster.

When switching resource is similarly scarce as vhost CPU resource, the algorithm gives bad estimate
(cap_f(MAX_SWITCH_CPU_SHARE) is too optimistic because PMs can't use that much CPU shares for packet switching).
In this case the program runs slower.

Patch: if a new branch is created because all PMs are stressed, then in share adjustment phase slash the counter?

The range of iv brute force is shrinked because the resource bound is usually tight.


## Test commands

```
./main.py -g input/graphs/1221.r0.cch.abr.graph -c input/graphs/1221_1053rnd.host -p input/pm/pms_01230123.txt --find-iv
```

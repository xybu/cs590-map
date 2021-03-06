Change Log
==========

The following changes have been made to the original UC-MKL.

## Changes to Stop Condition

We have made the following adjustments to stop condition:

1. K'-1

2. When an Assignment Appears Twice

### K'-1

The original UC-MKL needs all chosen `K'` PMs to be "fully utilized" to stop.
However, it's reasonable that the least powerful chosen PM is under utilized.
So we relax the condition and allow one PM to be under-utilized.

### When an Assignment Appears Twice

We observed that an assignment appearing twice indicates a loop will happen
(see below). So we simply stop. **Note that we do need a routine to evaluate
how better a new assignment is compared to an old assignment to make sure
iteration evolves.**

### Follow-up Question

1. What about the case where two PMs have utilization 88% and 89% (say, 90% is
the threshold). It may not be very different from (actually it could perform
better than) a case such as (90%, 87%).

2. For the case where there is not enough power for the mapping, all PMs can be
over-utilized. What can be a proper stop condition for this?

3. Another reasonable stop condition is when there is no PM that is under utilized.
Of course more iterations could move some workload from over-utilized PMs to "OK" PMs,
but it is not clear to what extent the new solution is better compared with the old
solution.

## Initial Values

Based on observations that 

 * It's unlikely to happen that a PM will have 90% of CPU share allocated for
   packet processing and 10% of CPU share for vhosts.

 * When a PM has 90% CPU share allocated for packet processing, the huge
   capacity will lead to a great number of vhosts assigned to it. This then
   will over-utilize this PM and the assignment is unacceptable. The algorithm
   will be dragged to the opposite extreme case. If there is no
   floor / ceiling CPU share restriction the algorithm will jump back and forth
   between the extreme cases; if there is such limit then the algorithm will be
   stuck in a fruitless loop that gives a sequence of assignments repeatedly
   (e.g., assignments 1, 2, 3, 4, 2, 3, 4, 2, 3, 4, ...).

After testing with expected average value (e.g., each PM uses
`total_CPU_share_of_vhosts / num_of_active_PMs`) and "most pessimistic" value
(e.g., each PM uses most CPU for vhosts and least for packet processing), it
turns out that the most pessimistic values work better as initial values --
instead of starting with 90% of CPU share allocated to packet processing, we use
a relatively small value like 10% (or whatever the floor value is). This way,
for each iteration the algorithm will "relax" the limit a little bit for more
capable PMs and gradually assign more and more hosts there.

## Moving Average

The effect of moving average in original UC-MKL is like -- it takes a few more iterations for the algorithm to jump back and forth between extreme cases; and 
because the change between two iterations is not too drastic, it _could_
stabilize in the middle.

To preserve the "damping effect" the moving average part is re-implemented as
something similar to RTT estimation of TCP:

```
next_cpu_share_for_pkt_processing = (1-a) * (share_so_far) + a * (share_for_this_round)
```

where `a` is a value in range `(0, 1]` and we use `0.6` for now.

It turns out that after the change on initial values the fluctuation among
iterations is no longer severe. It remains to be examined how the new moving
average calculation contributes to the algorithm.

## Fixing MKL

MKL may assign nodes to a set whose target weight is 0 (see original case study 80). This means that vhosts can be assigned to a PM that is thought as not
needed or not existent. To address the problem, a post-assignment check is added
in which nodes assigned to disabled PMs will be moved to the least stressed PM
(the one currently uses least CPU). Note that disabled PMs can differ among
iterations.

Based on observations so far, this situation happens when most sets are already
"overflown" and happens to "trivial" leaf nodes. There could be a better PM
to place such vhosts but using the least stressed PM should safely work.

## Update Involved PMs Only

The original UC-MKL updates CPU share for packet processing for all PMs 
regardless of whether it is disabled / existent or not. That is, it will
do

```
for each PM i:
    next_round_CPU_share_for_switch = MAX_CPU_SHARE - sum_of_CPU_share_used_by_vhosts
```

for all PMs. This to some extent leads to the problem recorded in [case_study_1221_realpm](case_study_no_moving_avg/case_study_1221_realpm), where
the program will in round `N` pick and overwhelm the most powerful PM and in round `N+1` pick and overwhelm the second most powerful PM and repeat `N` and
`N+1` (if allowed to run forever).

We changed it so that this update will skip PMs not chosen in this round (i.e., a PM not used in this round, or a PM that simply does not exist).

## Validate Capacity Functions?

The capacity function "0 17600 -235200" is not valid because part of its
codomain is negative on the domain. A valid function should be f(x): [0, 100] ->
R+. Since this is largely a problem from calculating regression functions,
the program (in Python wrapper) will automatically detect the min value at which
the function is valid.

## 0/1 Knapsack Limit

A fundamental problem with UC-MKL is that the decision made at each step uses
only partial information -- when deciding the goals for each set it uses only
capacity functions, and when checking CPU usage it uses only vhost CPU
requirements. To deal with the issue, we add another limit calculated from
CPU requirements -- the 0/1 Knapsack value for the available CPU share (KS
capacity), the weights of nodes (KS profit), and the vhost CPU requirements (KS
cost). This can give a rough upperbound for the max value for each goal. In
other words, 0/1 Knapsack tries to answer the question "What's the max possible
sum of vertex weight that a% CPU share budget can deal with?" Any excessive
capacity beyond this value will only lead to over-utilization of this PM.

It turns out that this limit only mitigates the issue. The reason is that while
say, 80%, CPU share means the max set weight cannot exceed, like, 10920, MKL
solver does not translate 10920 back to 80% -- for example, it can choose a few
nodes whose sum of weight is 100 and sum of CPU requirement is 10, instead of
choosing one node whose weight is 100 and sum of CPU requirement is 1 (which is
of better value from knapsack solver).

### Follow-Up

1. We could calculate the KS limit based on a coarsened version of the original
graph. This should give better values because some nodes are "bundled". But
(1) we can't use the MKL-coarsened graph because it happens after the goals are
decided, and (2) if we dynamically coarsen the graph, we cannot precompute the
KS limits.

2. With this KS limit it's not that important to use "most pessimistic" values
as starting point (see Initial Values section) anymore. Sometimes using an
initial value to make KS limit smaller works better. There should be a point
to balance capacity and KS limits -- to be explored.

A follow-up to [case_study_1221_realpm](../case_study_1221_realpm). It changed the algorithm so that only the PMs involved 
in current iteration will be updated.

With this change, the program is able to allocate the topology to two PMs, but the result is still wrong. The program
should pick up at least three PMs.

```
PM 0 is disabled in this iteration.

PM 1 is disabled in this iteration.

PM 2 is over-utilized. Its CPU usage is 143 + 10 = 153.
  |- Accum. usage=10.00, New usage=10.00, Next usage=10.

PM 3 is over-utilized. Its CPU usage is 267 + 10 = 277.
  |- Accum. usage=10.00, New usage=10.00, Next usage=10.
  
Iteration 1 gives same assignment as 0. Stop.
```

The program thinks that PM #2 and #3 can well address the topology because the sum of their capacity at 10% CPU share for packet processing exceeds sum of vhost weights but they can't. And it's a situation where the program cannot make progress.

## Thoughts

The algorithm applies capacity requirement and vhost CPU requirement on two disjoint steps. This lack of information on each 
step prevents the algorithm from making better decisions. For example, the calculated capacity value can be considered 
impractically large if the maximum node weight that can be fulfilled with the host CPU share budget is smaller. Therefore, the general direction is to take both requirements into consideration in every step.

Here are some potential solutions.

### 0/1 Knapsack

The idea comes from this observation:

For PM #3 whose capacity function is `4.459100 u^2 + 1267.184800 u + 948.392517` it calculates a capacity of `28075` with 20% CPU share allocated to switch and 80% CPU share available for vhosts. The sum of vertex weight is smaller -- `23080`. 
So what's the max possible sum of vertex weight that 80% CPU share budget can deal with?

We model the question into a 0/1 knapsack problem -- each vhost node is an item, with its CPU requirement the _cost_ of the
item and its node weight the _profit_ of the item. The CPU share available for vhosts on this PM is the _budget_ (or 
_capacity_). We want to maximize the profit subject to the budget.

It turns out that with 80% CPU budget, the max possible weight sum is `10920`. So any excessive capacity beyond this value
will only lead to over-utilization of this PM.

#### Evaluation

The problem with this solution is that, with `80%` CPU budget the max possible weight sum is `10920`, but `10920` does not
convert back to `80%` budget when partitioning. For example, Knapsack solver can pick a vhost `{5: cpu=3, weight=450}`,
but MKL can choose a few other nodes so that their weight sum is 450, but this choice makes the sum of CPU requirement
way above 3. As a result, this change only mitigates the issue (with this implementation the program now picks up 3 PMs
rather than 2 PMs).

#### Improvement

1. Maybe it works better on coarsened graph?

2. With this KS limit it's not that important to use "most pessimistic" values
as starting point (see CHANGELOG.md).

### Converting CPU requirement to capacity requirement

### Reduce MAX_CPU for PMs dynamically

This should be a very ugly and heuristic approach.

When to reduce? Reduce which PM? What's the lower bound?

### Change underlying algorithm to a multi-constraint solver

Some links:

1. [A New Algorithm for Multi-objective Graph Partitioning](http://link.springer.com/chapter/10.1007/3-540-48311-X_42)

### Pessimistic Approach -- Start with K PMs, then K-1, K-2, ...

Note that min number of PMs needed is ceiling(sum_of_cpu_req / 100). Force this and let the program start there.

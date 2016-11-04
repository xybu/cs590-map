We have been having trouble determining the value of K' (the min number of PMs needed) as input but determining K' is kind of critical. There are two directions:

1. Find a mathematically provable way of determining K' if used as input.
2. Try with some initial K' value, and use the output as feedback to determine what a better K' could be (feedback heuristic).

## Problem Formulation

The question is something like this: given the capacity and CPU shares of PMs, we want to find a smallest subset of PMs that can accomodate the topology.

| PM       | PM #1 | PM #2 | ... | PM #k | Total Required              |
| -------- | ----- | ----- | --- | ----- | --------------------------- |
| Capacity | W1    | W2    | ... | Wk    | W = Sum of vertex weight.   |
| CPU      | C1    | C2    | ... | Ck    | C = Sum of vhost CPU share. |

What's the smallest subset of PMs `P = {PM #a, PM #b, .. PM #k'}` that can satisfy all three conditions below:

1. 1 <= k' <= k
2. Sum of W_x, x in P, >= W
3. Sum of C_x, x in P, >= C

Can we determine the size of `P`, that is, `|P|`?

Can we determine the elements of `P`?

If we can't, can we at least give a lower bound for the value of `|P|`?

For example, given

| PM       | PM #1 | PM #2 | PM #3 | PM #4 | Total Required |
| -------- | ----- | ----- | ----- | ----- | -------------- |
| Capacity | 3536  | 1792  | 9127  | 14066 | 23080          |
| CPU      | 90    | 85    | 80    | 85    | 510            |

What's the min number of PMs that can satisfy the total required? What are they?

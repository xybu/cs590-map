TBA: Everything not yet categorized about METIS.

Input? Output? Refinement process? Criteria? Stop conditions?

Hopefully things will go clearer as we proceed.

## The Overall Logic

In UC-MKL the objective of the outer loop is to _try_ enforcing the CPU
constraint. But with METIS, which can solve two constraints together fairly
well, the check is no longer important.

So we will use the outer loop to refine the result.

Some heuristics we could inherit:

1. If a PM has unused CPU share, increase its capacity and/or vhost CPU share
(by what? Provided that it will reduce min cut?). Reserve, say 50%, of unused
share, and allocate the other 50% to both capacity and vhost. They divide the
share proportional to current CPU usage.

2. If a PM is over-utilized, decrease its capacity and/or vhost CPU share. Check
what's the culprit and then decide.

## K prime

Could remove PMs more aggressively.

## Branch for Over-Utilization

General direction is to use some global view = {PM limits, input shares, assignment, share usages} of all machines to
decide how to adjust the shares.

Another way that takes more info into consideration:
First deal with over PMs. Move its shares to non-over PMs. Then check if other PMs are under -- for those PMs we further
increase shares.

## Upper bound for min cut

As long as the assignment doesn't stress any edge, the edge cut is acceptable.

## Assignment classification

Tier 1 - no over-utilization, edge cut acceptable. Pick min cut.
Tier 2 - no over, edge cut too large. Pick min cut.
...



## Redundancy

Take into consideration in input -- worst case input -- average case input? In algorithm?

## Load Imbalance Vector

METIS takes a vector that specifies how much deviance we are going to tolerate for each constraint (pg.4 of the METIS 
algorithm paper). For now we use 1.0 for capacity constraint and 1.2 for CPU constraint but we should tune this parameter.


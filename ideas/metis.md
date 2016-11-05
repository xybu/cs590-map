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

## Load Imbalance Vector

METIS takes a vector that specifies how much deviance we are going to tolerate for each constraint (pg.4 of the METIS 
algorithm paper). For now we use 1.0 for capacity constraint and 1.2 for CPU constraint but we should tune this parameter.


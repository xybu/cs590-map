TODO
====

## Determine K'.

We need a mathematically provable way to determine K' (the min number of PMs
needed) if we are going to use that as input.

Thoughts:

1. Use output of an iteration to determine if a bigger or smaller K' is needed.
Basically treat K' as output and brute force K'.

2. Any heuristics? (e.g., Sort PMs by descending capacity or vhost CPU
availability and use the other constraint to exclude some PMs?)

## (METIS) The outer loop logic must be changed.

METIS (single-objective, multi-constraint solver) is really a game changer.

In UCMKL the objective of the outer look is to _try_ enforcing the CPU
constraint. But with METIS, which can solve two constraints together fairly
well, the check basically becomes useless. METIS usually gives decent assignment
that satisfies both constraints.

The goal of doing iterations is to refine the assignment, but in what aspects?
And when can it stop?

Some heuristics we could inherit:

1. If a PM has unused CPU share, increase its capacity or vhost CPU share
(by what? Provided that it will reduce min cut?). Basically to optimize the
under-utilized portion.

2. If a PM is over-utilized, decrease its capacity or vhost CPU share. Similar
to 1.

And something similar can be done to capacity requirement as well.

## Try optimizing the boundary vertices?

Basically take what METIS' refinement step does but focus on better utilizing
the PMs (which basically means refining the constraints rather than adhering
to it).

## (METIS) Tolerance Vector

How much deviance are we going to tolerate for capacity constraint?

## Redefine CPU share.

... so that we can unify the meaning of "1%" on a 4-core CPU and on a 2-core
CPU. Ideally we want the number to be comparable across all PMs, which may need
benchmarking.


# cs590-map

Some research work on network testbed mapping problem, with emphasis on mapping network experiments to heterogeneous
clusters.

## Outstanding Questions

* [How to incorporate information about link delay in edge weight?](ideas/edge_weight.md)
* [Can we properly determine K' as input?](ideas/kprime.md)
* [Refine CPU share value.](ideas/cpu_share.md)
* [Refine definition for capacity functions.](ideas/cap_func.md)
* [Design the logic that can make best use of what METIS offers.](ideas/metis.md)

## Summary

We explored UC-MKL to its limit and are exploring a solution based on METIS.

### Utilities

1. [Tool to visualize Chaco graph and assignments](visualize/).

### UC-MKL

 1. [How to use UC-MKL (input format)](UC-MKL/README.md).
 2. [Summary of Changes we have made to UC-MKL](UC-MKL/CHANGELOG.md)
 3. We instrumented UC-MKL code to record all intermediate states the program will go over.
  1) [Cases](UC-MKL/case_study_original) based on Rocketfuel graphs showed that UC-MKL repeated itself in most iterations.
  2) [Case](UC-MKL/case_study_kprime-1) that allowed 1 PM to be under-utilized.
  3) [Cases](UC-MKL/case_study_no_moving_avg) that studied the effect of moving average, initial values, and stop conditions.
  4) [Case](UC-MKL/case_study_1221_realpm) that tried the fixes on real PM functions. In this case UC-MKL will "over-estimate" the power of PMs and stubbornly put the whole topology on one PM.
  5) [Case](UC-MKL/case_study_1221_realpm_tryfix) in which we tried to let UC-MKL use information about both capacity constraint and vhost CPU constraint to determine K'. The 0/1 Knapsack model improved the estimation but to a very limited extent. It's a fundamental problem that UC-MKL cannot make use of all information at each step. We proposed [more ways to address it](UC-MKL/case_study_1221_realpm_tryfix). Some are ugly heuristics. We decided to resort to METIS.

### PyWrapper

To better compare UC-MKL (Chaco) with METIS, we extracted most logic to a wrapper program written in Python, and slightly modified the original Chaco so that it takes a list of goals (set weights) as additional input. We refer to this modified Chaco as _Chaco oracle_.

Then we supported METIS API in this wrapper program so METIS becomes another oracle. But as we dive deeper into METIS, we realized that this single-objective, multi-constraint solver will change the whole game. To unleash the full potential of METIS, basically the whole logic will be redesigned.

 1. [The wrapper program](/testbed_mapping).
 2. [A brief summary of TODOs](/testbed_mapping/TODO.md).
 3. Use the wrapper to compare UC-MKL and METIS with the only independent variable being the oracle program.

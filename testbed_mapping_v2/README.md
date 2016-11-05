Basically this version is designed exclusively for METIS.

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
 * `MAX_CPU_SHARE`: the maximum CPU shares (usually NCores * 100; use a smaller value to represent system overhead).
 * `MIN_SWITCH_CPU_SHARE`: reserve no less than this amount of CPU share to packet processing on the PM.
 * `MAX_SWITCH_CPU_SHARE`: reserve no more than this amount of CPU share to packet processing on the PM.
 * `0` <= <= `MIN_SWITCH_CPU_SHARE` <= `MAX_SWITCH_CPU_SHARE` <= `MAX_CPU_SHARE`.
 * `c_0` ... `c_m` are the coefficients for the capacity function. `f(u) = c_0 + c_1 * u + c_2 * u^2 + ...`. We require that the function cannot always evaluate to 0.

The numbers can be separated by spaces or tabs. Empty lines or lines starting with `#` will be ignored.

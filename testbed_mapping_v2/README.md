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
 * `MAX_CPU_SHARE`: the maximum CPU shares (usually 100xNCores; use a smaller value to represent system overhead).
 * `MIN_SWITCH_CPU_SHARE`: Use no less than this amount of CPU share to packet processing on the PM.
 * `MAX_SWITCH_CPU_SHARE`: Use no more than this amount of CPU share to packet processing on the PM.
 * `0` <= `MIN_SWITCH_CPU_SHARE` <= `MAX_SWITCH_CPU_SHARE` <= `MAX_CPU_SHARE`.
 * `c_0` ... `c_m` are the coefficients for the capacity function. `f(u) = c_0 + c_1 * u + c_2 * u^2 + ...`. We require that the function cannot always evaluate to 0.

The numbers can be separated by spaces or tabs. Empty lines or lines starting with `#` will be ignored.

## Rationale

At the lowest level, this program leverages METIS API to perform single-objective, multi-constraint partitioning.

### Starting Point

The first iteration uses the following initial values:

 * All PMs are chosen.
 * Each PM is allocated `constants.INIT_SWITCH_CPU_SHARES` (default: 20) or `MIN_SWITCH_CPU_SHARE` percent CPU, whichever is greater, for packet processing.
 * Rest of the CPU share is allocated to fulfill vhost CPU requirements.
 * Load imbalance tolerance for switch capacity constraint is `constants.SWITCH_CAPACITY_IMBALANCE_FACTOR` (default: 0 = no tolerance).
 * Load imbalance tolerance for CPU constraint is `constants.VHOST_CPU_IMBALANCE_FACTOR` (default: 0.1).

### Iterations

The program has an internal task queue to save the configurations that should be tried, and a hash set that saves the configurations that have
been tried along with the objective values (edge cut) obtained.

Each iteration performs as follows:

 1. Convert the switch CPU share values to switch capacity share values.
 2. Normalize the absolute share values to portions (shares summing up to 1).
 3. Call METIS k-way partition API and obtain the min cut and assignment result.
 4. Calculate how much switch and CPU weights are assigned to each PM.
 5. For each PM, do the following:
     1. Calculate the actual CPU shares needed to provide the assigned switch capacity because
        the capacity assigned may not equal the capacity provided as input. The actual CPU shares needed
        can be either more or less than the CPU shares we used in input. Note that if we change the input
        CPU share to this value with everything else the same the result will remain the same.
     2. Calculate the CPU shares used and unused.
     3. Calculate the weight factors for switch capacity and CPU constraints.
        For example, if total vhost CPU shares needed is 150 and a PM gets 50 vhost CPU assigned,
        then its weight factor for vhost CPU constraint is 50/150=0.33. 
 6. Record the assignment and input signature.
     1. We can further improve the input signature by treating two PMs with same parameters as equal.
        This way when eliminating PMs the program will not calculate setups that are actually equal twice.
        **TODO**.
 7. Adjustments based on the assignment result.
     1. Unneeded PM elimination. Find the PM that takes the least load. If its load can be fulfilled by the
        unused shares of other PMs then this PM is not needed. Here we take
        an assumption that the capacity function to some extent reflects the PM performance -- to provide
        equal amount of switch capcity, a weaker PM uses more CPU shares. The reason why this PM takes
        least weight is usually its inferior performance, so if it can use, say, 15% CPU share to provide,
        say, 5000 capacity, then other PMs will be able to provide 5000 capacity with no more than 15% CPU.
        So if other PMs have enough CPU shares to cover the vhost CPU shares and this 15% switch CPU share,
        then this PM is not needed. Unneeded PMs are usually eliminated in the earliest rounds. Some further
        thoughts:
         1. Note that there is chance that an unneeded PM may not be eliminated because of the CPU 
            estimation. We change it so that the PM is removed as long as its vhost weight can be covered
            by free CPU shares -- this could slightly stress other PMs and may NOT guarantee to produce best result.
            Corner cases like this, however, are very hard to trigger. In practice this usually means the PM is
            removed earlier than when we used total weight.
         2. If all PMs used are stressed and we have unused PMs the last removed PM will be brought back and set sticky.
         3. We can use the heuristics we thought of before to determine if this step is needed. E.g., the
            min number of PMs needed (NOTE: THIS IS NOT TRUE!) -- but what if overloading PMs results in better edge
            cut? **TODO**.
     2. CPU share adjustment. We distinguish three situations:
         1. The least utilized PM. **TODO**. If not "sticky" then we bias towards eliminating it by
            __what__? If sticky then we treat it the same as any under-utilized PM.
         2. Under-utilized PMs. If the unused CPU share exceeds the threshold specified by
            `constants.PM_UNDER_UTILIZED_THRESHOLD` (e.g., 10% unused shares = 0.1) then a PM is 
            under-utilized. Among the unused shares, we reserve a portion specified by
            `constants.PM_UNDER_UTILIZED_PORTION_RESERVE_RATIO` (default: 0.7) and say the remaining portion
            "free shares". We then allocate the free shares to switch CPU and vhost CPU shares proportional 
            to their current **usage**. Switch CPU share value is subject to the cap function domain defined
            by the PM. If the next vhost CPU share is less than previous vhost CPU share, we use the 
            previous value instead (or max_cpu_shares - switch shares, whichever is smaller). For example,
            if old  setup is (sw=10, vhost=70, max=100), then free shares = (1-0.7)*(100-80)=6.
            next_sw=6+ceil(6*(10/70))=6+1=7. next_vhost=70+(6-1)=75. Because 75+7=82<100, no capping will
            be done.
         3. Over-utilized. **TODO**. We cap its vhost CPU share to the max possible vhost CPU share scaled
            up by half of over utilization threshold. That is,
            `(pm.max_cpu_share - next_sw_cpu_share) * (1 + constants.PM_OVER_UTILIZED_THRESHOLD / 2)`.
 8. Stop conditions. The algorithm will NOT add a new task unless
     1. It's the first iteration.
     2. Edge cut is reduced in this round (we may do better by adjusting the params).
     3. A PM is eliminated.
     4. The input signature has not been tried before.

### Best Assignment Determination

When there is no more iterations to do the program prints all assignments attempted
and print a best assignment. Current criteria for "best" is min edge cut. **TODO**.


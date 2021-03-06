# Demonstration

We will demonstrate the program by showing results of partitioning some well-established topologies onto some heterogeneous physical machines, and comparing the results against the following baselines:

1. Balanced partitioning: Partition the graph into `N` sets whose sums of vertex weight are roughly equal, and assign set `i` to PM `#i`. This partition does not consider CPU share requirement. It's used in ... (what software?).

2. `MAX_CPU_SHARE` partitioning: Partition the graph into `N` sets so that the sum of CPU shares needed by vertices in set `i` is proportional to `MAX_CPU_SHARE` of PM `#i`, the maximum CPU share available on PM `#i`. For example, if PM #0 has max CPU share of 200 and PM #1 has 400, then the ratio of sums of CPU shares needed of vertices assigned to PM #0 and PM #1 is 1:2. This partition considers only CPU share requirement and ignores capacity requirement. It's used in ... (what software?).

3. C(90%) partition: Partition the graph into `N` sets so that the sum of vertex weight of set `i` is proportional to the value `capacity_func(0.9 * MAX_CPU_SHARE)`, where `capacity_func` is the capacity function of PM `#i`, and `MAX_CPU_SHARE` is the maximum CPU share of PM `#i`.

For all baselines the objective for partitioning is also to minimize the edge cut. We do the partitioning with METIS.

Recall that in our graph model, each node has two weights -- by "vertex weight" we mean the capacity weight of the vertex, and by "CPU weight" we mean the CPU shares needed by the vertex.

Other notes regarding our simulation are:

1. The PMs we have are too powerless to host some graphs (e.g., they need to be 100X faster to host the Rocketfuel graph). In this case we scale up all capacity functions so that the performance available and performance needed are at the same level.

2. For each vertex, we assign CPU requirement proportional to its degree, plus or minus one or two shares randomly. However, the number will be no less than 0.


## Rocketfuel Topology 1221 (Enough Resource)

The topology file [`1221.r0.cch.abr.graph`](demo/1221.r0.cch.abr.graph) has a total of `318` vertices and `758` edges. Total vertex weight is `23080` and total edge weight is `11540`. The CPU share requirements we assign to vertices sum up to `1053`.

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221.r0.cch.abr.graph.svg)

Six candidate PMs are used (note that we reserve 10 shares on each PM to represent overhead from other applications running on the PM):

```
<PM #0 | (2, 180)/190 | f(u) = 0.0199 u^2 + 199.6030 u^1 + -294.3504 u^0>   # 2core@1.20GHz
<PM #1 | (7, 180)/190 | f(u) = 0.2121 u^2 + 252.4785 u^1 + -1532.9436 u^0>  # 2core@1.86GHz
<PM #2 | (10, 180)/190 | f(u) = 0.4478 u^2 + 294.6084 u^1 + -2789.6768 u^0> # 2core@2.39GHz
<PM #3 | (0, 360)/390 | f(u) = 0.3728 u^2 + 116.5081 u^1 + 4188.2548 u^0>   # 4core@1.20GHz
<PM #4 | (0, 360)/390 | f(u) = 0.4720 u^2 + 186.2437 u^1 + 2707.8162 u^0>   # 4core@1.86GHz
<PM #5 | (0, 360)/390 | f(u) = 0.2880 u^2 + 329.0318 u^1 + 949.3183 u^0>    # 4core@2.39GHz
```

[PM Input](demo/pms_six_scaled_by_100.txt) | [CPU Requirement Input](demo/1221.1053rnd.host) | [Program command](demo/1221-1053rnd-6pms/COMMAND) | [Program output](demo/1221-1053rnd-6pms/output.txt) | [6PMs Baseline](demo/1221-1053rnd-6pms/baseline.txt) | [3PMs Baseline](demo/1221-1053rnd-6pms/baseline_3pm.txt)

### Our assignment

Our program stopped searching for better assignments after 7 iterations. It eliminates PMs #0-#2 and chooses PMs #3-#5.

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221-1053rnd-6pms/assignment_5.svg)

Because our baselines do not eliminate unneeded PMs, we generate baseline results not only with the same PM input we give to our program, but also with only the PMs chosen by our program.

Result of balanced partitioning with PMs #3-#5:

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221-1053rnd-6pms/assignment_BALANCED_3PMs.svg)

Result of MAX_CPU_SHARE partitioning with PMs #3-#5:

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221-1053rnd-6pms/assignment_MAX_CPU_SHARE_3PMs.svg)

Result of C(90%) partitioning with PMs #3-#5:

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221-1053rnd-6pms/assignment_C90_CAPACITY_3PMs.svg)

Graphs for 6-PMs baselines are not shown here (accessible [here](demo/1221-1053rnd-6pms)).

### Comparison

In the table we represent CPU usages as `sw/vh/used/max`, in which
1. `sw` is the CPU shares needed by packet switching
2. `vh` is the CPU shares needed by the vhosts (vertices)
3. `used` is the total CPU shares used on the PM
4. `max` is the max CPU shares of the PM.

| Partition ID | Min cut | PM #0 (2C 1.2G) | PM #1 (2C 1.86G) | PM #2 (2C 2.39G) | PM #3 (4C 1.2G) | PM #4 (4C 1.86G) | PM #5 (4C 2.39G) |
|--------------|---------|----------------|----------------|----------------|----------------|----------------|----------------|
|     Ours     |   580   |        -       |        -       |        -       | 26/303/329/390 | 25/369/394/390 | 22/381/403/390 |
|  BAL / 6PMs  |  2580   | 21/195/216/190 | 21/128/149/190 | 23/245/268/190 | 0/178/178/390  | 6/163/169/390  | 9/144/153/390  |
|  MCS / 6PMs  |  2140   | 11/114/125/190 | 14/113/127/190 | 20/115/135/190 | 12/241/253/390 | 20/241/261/390 | 10/229/239/390 |
|  C90 / 6PMs  |  2140   | 12/71/83/190   | 17/102/119/190 | 19/130/149/190 | 0/181/181/390  | 11/252/263/290 | 19/317/336/390 |
|  BAL / 3PMs  |   700   |        -       |        -       |        -       | 28/307/335/390 | 26/373/399/390 | 21/373/394/390 |
|  MCS / 3PMs  |   850   |        -       |        -       |        -       | 31/354/385/390 | 25/339/364/390 | 20/360/380/390 |
|  C90 / 3PMs  |   500   |        -       |        -       |        -       | 9/264/273/390  | 27/350/377/390 | 27/439/466/390 |

We see that our partition result is better than any baseline partitions using 6 PMs because it achieves smaller min cut with roughly half of the resource. For 3-PMs baselines, compared to balanced partitioning (BAL) and MAX_CPU_SHARE partitioning (MCS) our partition achieves smaller min cut and the resource allocation is more coherent to the processing power of PMs. Result of C(90%) partition (C90) is not desirable in practice because PM #5 is heavily overloaded, which implies loss of fidelity.

## Rocketfuel Topology 1221 (Lacking Resource)

In this simulation, we show that our algorithm does best effort partitioning when processing power is not enough.

Input is the same as previous case, except that instead of providing 6 PMs, we pick 3 of them, resulting in lack of resource:

```
<PM #0 | (2, 180)/190 | f(u) = 0.0199 u^2 + 199.6030 u^1 + -294.3504 u^0>   # 2core@1.20GHz
<PM #1 | (0, 360)/390 | f(u) = 0.3728 u^2 + 116.5081 u^1 + 4188.2548 u^0>   # 4core@1.20GHz
<PM #2 | (0, 360)/390 | f(u) = 0.2880 u^2 + 329.0318 u^1 + 949.3183 u^0>    # 4core@2.39GHz
```

[PM Input](demo/pms_three_scaled_by_100.txt) | [CPU Requirement Input](demo/1221.1053rnd.host) | [Program command](demo/1221-1053rnd-3pms/COMMANDS) | [Program output](demo/1221-1053rnd-3pms/output.txt) | [Baseline output](demo/1221-1053rnd-3pms/baseline.txt)

### Our assignment

It takes 3 iterations for our program to stop. It picks all PMs and give a min cut of 670.

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221-1053rnd-3pms/assignment_0.svg)

Graph of balanced partitioning is the same as that of balanced partitioning in previous case.

Result of MAX_CPU_SHARE partitioning:

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221-1053rnd-3pms/assignment_MAX_CPU_SHARE_3PMs.svg)

Result of C(90%) partitioning:

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221-1053rnd-3pms/assignment_C90_CAPACITY_3PMs.svg)

### Comparison

| Partition ID | Min cut | PM #0 (2C 1.2G) | PM #1 (4C 1.2G) | PM #2 (4C 2.39G) |
|--------------|---------|----------------|----------------|----------------|
|     Ours     |   670   | 25/187/212/190 | 35/426/461/390 | 27/440/467/390 |
|  BAL / 3PMs  |   700   | 40/307/347/190 | 28/373/401/390 | 21/373/394/390 |
|  MCS / 3PMs  |   580   | 22/201/223/190 | 42/436/478/390 | 26/416/442/390 |
|  C90 / 3PMs  |  1020   | 20/134/154/190 | 21/337/358/390 | 35/582/617/390 |

We see that there is a PM heavily overloaded in balanced partitioning (BAL) and C(90%) partitioning (C90) -- utilization of PM #0 in BAL exceeds its maximum by 82% and utilization of PM #2 in C90 exceeds by 58%. BAL fails because it does not consider the performance discrepancy of PMs and C90 fails because it over-estimates the performance discrepancy. By contrast, our partition deals with lack of resource by overloading PM #0 by about 12%, and PM #1 by 18%, and PM #2 by 20%, which should have smaller impact on fidelity in general.

Although it may depend on the actual experiment to determine whether or not our partition is better than MAX_CPU_SHARE partition (MCS), our partition result makes more sense in that (1) it tries to avoid overloading the weakest PM because fidelity may be worse otherwise, and (2) PMs with higher performance get more load automatically, while in MCS the experimenter must first realize that the experiment can be better off by swapping the partitions on PM #1 and PM #2, then do so manually. When there are more PMs involved, such kinds of "optimization-by-eyes" may become less obvious, which makes it more desirable to do so automatically.

## Jellyfish Topology

TODO: Cite some characteristics about the topology from Jellyfish paper: [http://pbg.cs.illinois.edu/papers/jellyfish-nsdi12.pdf](http://pbg.cs.illinois.edu/papers/jellyfish-nsdi12.pdf).

The topology file [`jellyfish-210sw.graph`](demo/jellyfish-210sw.graph) has a total of `210` vertices and `630` edges. Total vertex weight is `27400` and total edge weight is `12600`. The CPU share requirements we assign to vertices sum up to `694`.

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/jellyfish-210sw.graph.svg)

We pick the same three PMs used in previous case:

```
<PM #0 | (2, 180)/190 | f(u) = 0.0199 u^2 + 199.6030 u^1 + -294.3504 u^0>   # 2core@1.20GHz
<PM #1 | (0, 360)/390 | f(u) = 0.3728 u^2 + 116.5081 u^1 + 4188.2548 u^0>   # 4core@1.20GHz
<PM #2 | (0, 360)/390 | f(u) = 0.2880 u^2 + 329.0318 u^1 + 949.3183 u^0>    # 4core@2.39GHz
```

[PM Input](demo/pms_three_scaled_by_100.txt) | [CPU Requirement Input](demo/jellyfish-210sw.694rnd.host) | [Program command](demo/jellyfish-210sw-694rnd-3pms/COMMANDS) | [Program output](demo/jellyfish-210sw-694rnd-3pms/output.txt) | [Baseline output](demo/jellyfish-210sw-694rnd-3pms/baseline.txt)

### Our assignment

The program takes 24 iterations and picks a partition with min cut 3400.

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/jellyfish-210sw-694rnd-3pms/assignment_12.svg)

Graphs for baseline partitions are not included because the topology is intrinsically random and visualizing them does not reveal interesting patterns.

#### Comparison

| Partition ID | Min cut | PM #0 (2C 1.2G) | PM #1 (4C 1.2G) | PM #2 (4C 2.39G) |
|--------------|---------|----------------|----------------|----------------|
|     Ours     |   3400  | 9/30/39/190    | 59/313/372/390 | 38/351/389/390 |
|  Ours (OC)   |   2980  |       -        | 64/329/393/390 | 40/365/405/390 |
|  BAL / 3PMs  |   3940  | 48/224/272/190 | 37/229/266/390 | 25/241/266/390 |
|  MCS / 3PMs  |   3860  | 26/133/159/190 | 49/276/325/390 | 33/285/318/390 |
|  C90 / 3PMs  |   3460  | 17/83/100/190  | 38/221/259/390 | 43/390/433/390 |

Result of balanced partitioning is not acceptable because PM #0 is overloaded by too much. While the result of MCS partition
is good enough, our result manages to further reduce edge cut by about 12% without sacrification. C90 partition has edge cut close to ours but PM #2 is overloaded by 11%, while in ours no PM is overloaded. Besides, if a smaller edge cut is preferred to in-range workload on PMs, by slightly relaxing the parameter controlling the degree to tolerate PM overloading, we obtain a better partition (OC) which not only achieves smaller min cut, but also eliminates PM #0, by overloading PM #1 by 0.8% and PM #2 by 3.8%. It takes 7 iterations for our program to finish the OC partition.

The two partitions given by our program reflects the flexibility of our algorithm to meet different priorities needed by different experiments.

## Fat Tree Topology

Fat-tree topology (intro here: http://courses.csail.mit.edu/6.896/spring04/handouts/papers/fat_trees.pdf)

The topology file [`fattree-151sw.graph`](demo/fattree-151sw.graph) has a total of `151` vertices and `660` edges. Total vertex weight is `13750` and total edge weight is `6600`. The total CPU share requirement by vertices is `567`.

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/fattree-151sw.graph.svg)

This time we pick the least and most powerful PMs on our list:

```
<PM #0 | (2, 180)/190 | f(u) = 0.0199 u^2 + 199.6030 u^1 + -294.3504 u^0>   # 2core@1.20GHz
<PM #1 | (0, 360)/390 | f(u) = 0.2880 u^2 + 329.0318 u^1 + 949.3183 u^0>    # 4core@2.39GHz
```

[PM Input](demo/pms_two_scaled_by_100.txt) | [CPU Requirement Input](demo/fattree-151sw.567rnd.host) | [Program command](demo/fattree-151sw-567rnd-2pms/COMMANDS) | [Program output](demo/fattree-151sw-567rnd-2pms/output.txt) | [Baseline output](demo/fattree-151sw-567rnd-2pms/baseline.txt)

### Our assignment

Our program stops after 7 iterations and the min cut is 1370. It also indicates that this setup does not have enough CPU resource
even though the number of CPU shares needed by vertices (567) is smaller than the sum of max CPU shares of PMs (600).

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/fattree-151sw-567rnd-2pms/assignment_0.svg)

Result of balanced partitioning:

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/fattree-151sw-567rnd-2pms/assignment_BALANCED_2PMs.svg)

Result of MAX_CPU_SHARE partitioning:

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/fattree-151sw-567rnd-2pms/assignment_MAX_CPU_SHARE_2PMs.svg)

Result of C(90%) partitioning:

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/fattree-151sw-567rnd-2pms/assignment_C90_CAPACITY_2PMs.svg)


### Comparison

| Partition ID | Min cut | PM #0 (2C 1.2G) | PM #1 (4C 2.39G) |
|--------------|---------|----------------|----------------|
|     Ours     |   1370  | 24/169/193/190 | 26/398/424/390 |
|      BAL     |   1650  | 36/291/327/190 | 18/276/294/390 |
|      MCS     |   1350  | 23/188/211/190 | 26/379/405/390 |
|      C90     |   1000  | 15/105/120/190 | 31/462/493/390 |

C90 partition gives the smallest min cut yet PM #1 is heavily overloaded while PM #0 is under-utilized. BAL partition does well in neither min cut nor load allocation (either set will overload PM #0 and neither set saturates PM #1). As for MCS and our partition result, MCS overloads PM #0 by 11% and PM #1 by 4% while ours overloads PM #0 by 2% and PM #1 by 8%. Depending on the actual experiment to conduct the effect of those two overload schemes may or may not vary, but in general we prefer the more powerful PM to take more load when resource is not enough.

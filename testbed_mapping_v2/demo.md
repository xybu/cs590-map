# Demonstration

We will demonstrate the program with some topology graphs. Because we don't have machines powerful enough to host some graphs, we may scale up the capacity functions so that the power reflected is on par with the performance needed.

## Rocketfuel Topology 1221

The topology file `1221.r0.cch.abr.graph` has 318 vertices and 758 edges. Total edge weight is 11540 and total vertex weight is 23080.

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221.r0.cch.abr.graph.svg)

### #PMs = 6, SUM(vHost_CPU_req)=1003

We assign each vertex a CPU share requirement proportional to the vertex degree and total CPU shares needed sums up to 1003.

The PM input is (our machines are outdated; we scaled the capacity function so that u->f(u) becomes u->100f(u) so that the switching capability of the machines and required by the graph are at the same scale)

```
# 2core@1.20GHz
<PM #0 | (2, 180)/190 | f(u) = 0.0199 u^2 + 199.6030 u^1 + -294.3504 u^0>
# 2core@1.86GHz
<PM #1 | (7, 180)/190 | f(u) = 0.2121 u^2 + 252.4785 u^1 + -1532.9436 u^0>
# 2core@2.39GHz
<PM #2 | (10, 180)/190 | f(u) = 0.4478 u^2 + 294.6084 u^1 + -2789.6768 u^0>
# 4core@1.20GHz
<PM #3 | (0, 360)/390 | f(u) = 0.3728 u^2 + 116.5081 u^1 + 4188.2548 u^0>
# 4core@1.86GHz
<PM #4 | (0, 360)/390 | f(u) = 0.4720 u^2 + 186.2437 u^1 + 2707.8162 u^0>
# 4core@2.39GHz
<PM #5 | (0, 360)/390 | f(u) = 0.2880 u^2 + 329.0318 u^1 + 949.3183 u^0>
```

Best assignment based on our criteria is

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221-1003-6pms/assignment_5.svg)

```
Assignment 5
  Min cut: 840
  Machines used:
    <PM #3 | (0, 360)/390 | f(u) = 0.3728 u^2 + 116.5081 u^1 + 4188.2548 u^0>
      CPU: switch_sh=27, vhost={u=291, sh=300}, total={u=317, sh=327}.
    <PM #4 | (0, 360)/390 | f(u) = 0.4720 u^2 + 186.2437 u^1 + 2707.8162 u^0>
      CPU: switch_sh=23, vhost={u=380, sh=390}, total={u=403, sh=413}.
    <PM #5 | (0, 360)/390 | f(u) = 0.2880 u^2 + 329.0318 u^1 + 949.3183 u^0>
      CPU: switch_sh=23, vhost={u=332, sh=333}, total={u=355, sh=356}.
  Machines excluded:
    <PM #1 | (7, 180)/190 | f(u) = 0.2121 u^2 + 252.4785 u^1 + -1532.9436 u^0>
    <PM #2 | (10, 180)/190 | f(u) = 0.4478 u^2 + 294.6084 u^1 + -2789.6768 u^0>
    <PM #0 | (2, 180)/190 | f(u) = 0.0199 u^2 + 199.6030 u^1 + -294.3504 u^0>
  Assignment of nodes:
    3, 5, 5, 4, 4, 5, 5, 5, 3, 5, 4, 3, 3, 3, 3, 3, 5, 3, 5, 3, 
    5, 3, 5, 3, 3, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 3, 
    5, 5, 5, 5, 3, 4, 5, 3, 5, 4, 4, 5, 5, 3, 3, 4, 4, 4, 4, 4, 
    4, 5, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 5, 5, 5, 3, 5, 5, 4, 3, 
    3, 3, 4, 4, 5, 5, 4, 4, 4, 5, 5, 4, 4, 4, 5, 5, 5, 3, 3, 3, 
    5, 5, 5, 3, 3, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 
    5, 5, 4, 3, 3, 3, 3, 5, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 
    5, 5, 3, 3, 5, 5, 5, 5, 3, 5, 5, 5, 4, 5, 5, 5, 5, 5, 5, 5, 
    5, 5, 3, 3, 5, 5, 5, 5, 5, 5, 4, 3, 5, 5, 5, 5, 5, 5, 3, 3, 
    5, 5, 3, 3, 3, 3, 3, 5, 3, 5, 5, 5, 5, 5, 5, 4, 5, 5, 5, 5, 
    5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 3, 5, 5, 5, 5, 5, 5, 
    5, 3, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 5, 5, 4, 3, 5, 5, 3, 5, 
    3, 5, 3, 3, 3, 3, 3, 5, 4, 3, 3, 5, 5, 3, 5, 5, 5, 3, 5, 5, 
    3, 3, 4, 4, 4, 4, 4, 3, 4, 4, 4, 4, 5, 5, 4, 5, 5, 5, 5, 3, 
    5, 5, 5, 3, 3, 5, 3, 5, 5, 5, 3, 5, 5, 5, 5, 5, 3, 3, 5, 3, 
    3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 5, 5, 3, 4, 4, 4, 4,
```
  
  We see that the program partitions the graph into the three most powerful PMs. However, note that PM #4, supposedly less powerful than PM #5, is assigned more workload. The reason is that the performance difference is not big enough to make a difference to the result given the constant parameters we chose. We can adjust the parameters to obtain better result -- e.g., min cut, load balancing, etc.

### #PMs = 3, SUM(vHost_CPU_req)=1003

This setup demonstrates how the program performs when PM resource is not enough (resource is roughly 80% of what's needed).

PMs chosen are:
```
# 2core@1.20GHz
<PM #0 | (2, 180)/190 | f(u) = 0.0199 u^2 + 199.6030 u^1 + -294.3504 u^0>
# 4core@1.20GHz
<PM #1 | (0, 360)/390 | f(u) = 0.3728 u^2 + 116.5081 u^1 + 4188.2548 u^0>
# 4core@2.39GHz
<PM #2 | (0, 360)/390 | f(u) = 0.2880 u^2 + 329.0318 u^1 + 949.3183 u^0>
```

Best assignment is

![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/demo/1221-1003-3pms/assignment_0.svg)

```
Assignment 0
  Min cut: 670
  Machines used:
    <PM #0 | (2, 180)/190 | f(u) = 0.0199 u^2 + 199.6030 u^1 + -294.3504 u^0>
      CPU: switch_sh=20, vhost={u=157, sh=170}, total={u=182, sh=190}.
    <PM #1 | (0, 360)/390 | f(u) = 0.3728 u^2 + 116.5081 u^1 + 4188.2548 u^0>
      CPU: switch_sh=20, vhost={u=402, sh=370}, total={u=437, sh=390}.
    <PM #2 | (0, 360)/390 | f(u) = 0.2880 u^2 + 329.0318 u^1 + 949.3183 u^0>
      CPU: switch_sh=20, vhost={u=444, sh=370}, total={u=471, sh=390}.
  Machines excluded:
  Assignment of nodes:
    1, 2, 1, 2, 2, 2, 2, 1, 0, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
    1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 
    1, 1, 1, 1, 0, 2, 1, 1, 2, 2, 2, 1, 1, 1, 1, 2, 2, 2, 2, 2, 
    2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 2, 0, 2, 2, 2, 1, 
    1, 1, 2, 2, 0, 1, 2, 2, 2, 0, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 
    2, 2, 2, 0, 1, 2, 1, 0, 0, 1, 2, 2, 1, 1, 1, 0, 0, 0, 0, 0, 
    0, 0, 2, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 
    1, 2, 1, 1, 0, 0, 2, 2, 1, 0, 0, 1, 2, 2, 0, 0, 0, 0, 0, 0, 
    0, 0, 0, 1, 1, 2, 0, 1, 1, 1, 2, 1, 2, 2, 2, 0, 0, 0, 0, 1, 
    0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 
    1, 1, 1, 1, 0, 2, 0, 0, 0, 0, 0, 0, 2, 1, 2, 2, 2, 2, 2, 2, 
    1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 1, 2, 2, 0, 2, 1, 0, 2, 
    1, 1, 1, 1, 1, 1, 1, 1, 2, 0, 1, 2, 2, 1, 2, 2, 2, 1, 1, 1, 
    1, 0, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 1, 0, 2, 0, 0, 0, 0, 1, 
    1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 
    1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 2, 2, 0, 2, 2, 2, 2,
```

We see that the amount of load assigned is roughly comparable to the performance of each PM. Also note that more powerful PMs are overloaded since the total resource cannot accommodate, and more capable PMs are overloaded more severely.


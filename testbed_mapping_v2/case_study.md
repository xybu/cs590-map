# Case Study: When Resource is Enough

```
xb@ubuntu:[~/Desktop/cs590-map/testbed_mapping_v2]: ./main.py -g input/1221.r0.cch.abr.graph -p input/pms_from_paper_7.txt -c input/1221_410.host

Namespace(graph_file='input/1221.r0.cch.abr.graph', pm_file='input/pms_from_paper_7.txt', vhost_cpu_file='input/1221_410.host')

Program parameters:
  EDGE_WEIGHT_KEY: weight
  NODE_SWITCH_CAPACITY_WEIGHT_KEY: weight
  NODE_CPU_WEIGHT_KEY: cpu
  SWITCH_CAPACITY_IMBALANCE_FACTOR: 0.1
  VHOST_CPU_IMBALANCE_FACTOR: 0.15
  INIT_SWITCH_CPU_SHARES: 20
  SWITCH_CPU_SHARE_UPDATE_FACTOR: 0.4
  PM_UNDER_UTILIZED_THRESHOLD: 0.1
  PM_UNDER_UTILIZED_PORTION_RESERVE_RATIO: 0.7
  PM_OVER_UTILIZED_THRESHOLD: 0.1

Graph stats:
  Number of vertices:     318
  Number of edges:        758
  Total edge weight:      11540
  Total vertex weight:    23080
  Total vhost CPU weight: 410

NOTE: Capacity function of PM #0 is not defined below 1. Input fixed.
NOTE: Capacity function of PM #1 is not defined below 1. Input fixed.
NOTE: Capacity function of PM #2 is not defined below 8. Input fixed.
Read 7 PMs from input:
  <PM #0 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  <PM #1 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>

********************************************************************************
********************************  Assignment 0  ********************************
********************************************************************************

sw_cpu_shares: [20, 20, 20, 20, 20, 20, 20]
sw_cap_shares: [7457.4763, 7457.4763, 9132.043400000002, 15343.1926, 15343.1926, 28075.7285, 28075.7285]
vh_cpu_shares: [80, 80, 80, 80, 80, 80, 80]
min_cut:       2280

PM Elimination Phase:
  Target PM: #0, sticky=False
  Total free CPU shares: 205
  Shares covered by PM:  45
  PM #0 will be excluded from next round.

********************************************************************************
********************************  Assignment 1  ********************************
********************************************************************************

sw_cpu_shares: [20, 20, 20, 20, 20, 20]
sw_cap_shares: [7457.4763, 9132.043400000002, 15343.1926, 15343.1926, 28075.7285, 28075.7285]
vh_cpu_shares: [80, 80, 80, 80, 80, 80]
min_cut:       1680

PM Elimination Phase:
  Target PM: #1, sticky=False
  Total free CPU shares: 109
  Shares covered by PM:  44
  PM #1 will be excluded from next round.

********************************************************************************
********************************  Assignment 2  ********************************
********************************************************************************

sw_cpu_shares: [20, 20, 20, 20, 20]
sw_cap_shares: [9132.043400000002, 15343.1926, 15343.1926, 28075.7285, 28075.7285]
vh_cpu_shares: [80, 80, 80, 80, 80]
min_cut:       1240

PM Elimination Phase:
  Target PM: #2, sticky=False
  Total free CPU shares: 51
  Shares covered by PM:  82
  No PM can be excluded from next round.

Share Adjustment Phase:
4: <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 6 / 20, Cap = 7400.0000 / 28075.7285
  Vhost  Used/Alloc:  CPU = 94 / 80
  Overall: CPU = 100 / 100
  Weights: sw = 0.3206, vcpu = 0.2293, total = 0.5499
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
3: <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 4 / 20, Cap = 5750.0000 / 28075.7285
  Vhost  Used/Alloc:  CPU = 94 / 80
  Overall: CPU = 98 / 100
  Weights: sw = 0.2491, vcpu = 0.2293, total = 0.4784
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
1: <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 20, Cap = 3970.0000 / 15343.1926
  Vhost  Used/Alloc:  CPU = 78 / 80
  Overall: CPU = 78 / 100
  Weights: sw = 0.1720, vcpu = 0.1902, total = 0.3623
  Under-utilized shares: 12. Adjustable shares: 3.
  Switch deltas: [0, 0, 1, 0, 0]
  Vhost deltas:  [0, 0, 2, 0, 0]
2: <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 20, Cap = 3550.0000 / 15343.1926
  Vhost  Used/Alloc:  CPU = 73 / 80
  Overall: CPU = 73 / 100
  Weights: sw = 0.1538, vcpu = 0.1780, total = 0.3319
  Under-utilized shares: 17. Adjustable shares: 2.
  Switch deltas: [0, 0, 1, 1, 0]
  Vhost deltas:  [0, 0, 2, 1, 0]
0: <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  Switch Used/Alloc:  CPU = 11 / 20, Cap = 2410.0000 / 9132.0434
  Vhost  Used/Alloc:  CPU = 71 / 80
  Overall: CPU = 82 / 100
  Weights: sw = 0.1044, vcpu = 0.1732, total = 0.2776
  Under-utilized shares: 8. Adjustable shares: 1.
  Switch deltas: [0, 0, 1, 1, 1]
  Vhost deltas:  [0, 0, 2, 1, 0]


********************************************************************************
********************************  Assignment 3  ********************************
********************************************************************************

sw_cpu_shares: [12, 1, 1, 4, 6]
sw_cap_shares: [3260.3337999999994, 4516.1413999999995, 4516.1413999999995, 6088.4773, 8712.0289]
vh_cpu_shares: [71, 80, 74, 94, 94]
min_cut:       940

PM Elimination Phase:
  Target PM: #2, sticky=False
  Total free CPU shares: 55
  Shares covered by PM:  87
  No PM can be excluded from next round.

Share Adjustment Phase:
4: <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 6 / 6, Cap = 8040.0000 / 8712.0289
  Vhost  Used/Alloc:  CPU = 103 / 94
  Overall: CPU = 109 / 100
  Weights: sw = 0.3484, vcpu = 0.2512, total = 0.5996
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
3: <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 4 / 4, Cap = 4900.0000 / 6088.4773
  Vhost  Used/Alloc:  CPU = 87 / 94
  Overall: CPU = 91 / 100
  Weights: sw = 0.2123, vcpu = 0.2122, total = 0.4245
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
2: <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 1, Cap = 4040.0000 / 4516.1414
  Vhost  Used/Alloc:  CPU = 77 / 74
  Overall: CPU = 77 / 100
  Weights: sw = 0.1750, vcpu = 0.1878, total = 0.3628
  Under-utilized shares: 13. Adjustable shares: 3.
  Switch deltas: [0, 0, 1, 0, 0]
  Vhost deltas:  [0, 0, 2, 0, 0]
1: <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 1, Cap = 3320.0000 / 4516.1414
  Vhost  Used/Alloc:  CPU = 68 / 80
  Overall: CPU = 68 / 100
  Weights: sw = 0.1438, vcpu = 0.1659, total = 0.3097
  Under-utilized shares: 22. Adjustable shares: 2.
  Switch deltas: [0, 0, 1, 1, 0]
  Vhost deltas:  [0, 0, 2, 1, 0]
0: <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  Switch Used/Alloc:  CPU = 12 / 12, Cap = 2780.0000 / 3260.3338
  Vhost  Used/Alloc:  CPU = 75 / 71
  Overall: CPU = 87 / 100
  Weights: sw = 0.1205, vcpu = 0.1829, total = 0.3034
  Under-utilized shares: 3. Adjustable shares: 1.
  Switch deltas: [0, 0, 1, 1, 1]
  Vhost deltas:  [0, 0, 2, 1, 0]


********************************************************************************
********************************  Assignment 4  ********************************
********************************************************************************

sw_cpu_shares: [13, 1, 1, 4, 6]
sw_cap_shares: [3994.2974999999997, 4516.1413999999995, 4516.1413999999995, 6088.4773, 8712.0289]
vh_cpu_shares: [75, 69, 79, 87, 100]
min_cut:       940

PM Elimination Phase:
  Target PM: #3, sticky=False
  Total free CPU shares: 36
  Shares covered by PM:  68
  No PM can be excluded from next round.

Share Adjustment Phase:
4: <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 6 / 6, Cap = 7940.0000 / 8712.0289
  Vhost  Used/Alloc:  CPU = 101 / 100
  Overall: CPU = 107 / 100
  Weights: sw = 0.3440, vcpu = 0.2463, total = 0.5904
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
3: <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 4 / 4, Cap = 5400.0000 / 6088.4773
  Vhost  Used/Alloc:  CPU = 92 / 87
  Overall: CPU = 96 / 100
  Weights: sw = 0.2340, vcpu = 0.2244, total = 0.4584
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
2: <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 1, Cap = 3540.0000 / 4516.1414
  Vhost  Used/Alloc:  CPU = 72 / 79
  Overall: CPU = 72 / 100
  Weights: sw = 0.1534, vcpu = 0.1756, total = 0.3290
  Under-utilized shares: 18. Adjustable shares: 5.
  Switch deltas: [0, 0, 1, 0, 0]
  Vhost deltas:  [0, 0, 4, 0, 0]
0: <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  Switch Used/Alloc:  CPU = 12 / 13, Cap = 2880.0000 / 3994.2975
  Vhost  Used/Alloc:  CPU = 77 / 75
  Overall: CPU = 89 / 100
  Weights: sw = 0.1248, vcpu = 0.1878, total = 0.3126
  Under-utilized shares: 1. Adjustable shares: 1.
  Switch deltas: [0, 0, 1, 1, 0]
  Vhost deltas:  [0, 0, 4, 0, 0]
1: <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 1, Cap = 3320.0000 / 4516.1414
  Vhost  Used/Alloc:  CPU = 68 / 69
  Overall: CPU = 68 / 100
  Weights: sw = 0.1438, vcpu = 0.1659, total = 0.3097
  Under-utilized shares: 22. Adjustable shares: 0.
  Switch deltas: [0, 0, 1, 1, 1]
  Vhost deltas:  [0, 0, 4, 0, 0]


********************************************************************************
********************************  Assignment 5  ********************************
********************************************************************************

sw_cpu_shares: [13, 1, 1, 4, 6]
sw_cap_shares: [3994.2974999999997, 4516.1413999999995, 4516.1413999999995, 6088.4773, 8712.0289]
vh_cpu_shares: [77, 68, 76, 92, 100]
min_cut:       940

PM Elimination Phase:
  Target PM: #3, sticky=False
  Total free CPU shares: 36
  Shares covered by PM:  68
  No PM can be excluded from next round.

Share Adjustment Phase:
4: <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 6 / 6, Cap = 7940.0000 / 8712.0289
  Vhost  Used/Alloc:  CPU = 101 / 100
  Overall: CPU = 107 / 100
  Weights: sw = 0.3440, vcpu = 0.2463, total = 0.5904
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
3: <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 4 / 4, Cap = 4900.0000 / 6088.4773
  Vhost  Used/Alloc:  CPU = 87 / 92
  Overall: CPU = 91 / 100
  Weights: sw = 0.2123, vcpu = 0.2122, total = 0.4245
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
2: <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 1, Cap = 4040.0000 / 4516.1414
  Vhost  Used/Alloc:  CPU = 77 / 76
  Overall: CPU = 77 / 100
  Weights: sw = 0.1750, vcpu = 0.1878, total = 0.3628
  Under-utilized shares: 13. Adjustable shares: 3.
  Switch deltas: [0, 0, 1, 0, 0]
  Vhost deltas:  [0, 0, 2, 0, 0]
0: <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  Switch Used/Alloc:  CPU = 12 / 13, Cap = 2880.0000 / 3994.2975
  Vhost  Used/Alloc:  CPU = 77 / 77
  Overall: CPU = 89 / 100
  Weights: sw = 0.1248, vcpu = 0.1878, total = 0.3126
  Under-utilized shares: 1. Adjustable shares: 1.
  Switch deltas: [0, 0, 1, 1, 0]
  Vhost deltas:  [0, 0, 2, 0, 0]
1: <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 1, Cap = 3320.0000 / 4516.1414
  Vhost  Used/Alloc:  CPU = 68 / 68
  Overall: CPU = 68 / 100
  Weights: sw = 0.1438, vcpu = 0.1659, total = 0.3097
  Under-utilized shares: 22. Adjustable shares: 0.
  Switch deltas: [0, 0, 1, 1, 1]
  Vhost deltas:  [0, 0, 2, 0, 0]


********************************************************************************
********************************  Assignment 6  ********************************
********************************************************************************

sw_cpu_shares: [13, 1, 1, 4, 6]
sw_cap_shares: [3994.2974999999997, 4516.1413999999995, 4516.1413999999995, 6088.4773, 8712.0289]
vh_cpu_shares: [77, 68, 79, 87, 100]
min_cut:       940

PM Elimination Phase:
  Target PM: #3, sticky=False
  Total free CPU shares: 36
  Shares covered by PM:  68
  No PM can be excluded from next round.

Share Adjustment Phase:
4: <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 6 / 6, Cap = 7940.0000 / 8712.0289
  Vhost  Used/Alloc:  CPU = 101 / 100
  Overall: CPU = 107 / 100
  Weights: sw = 0.3440, vcpu = 0.2463, total = 0.5904
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
3: <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 4 / 4, Cap = 4900.0000 / 6088.4773
  Vhost  Used/Alloc:  CPU = 87 / 87
  Overall: CPU = 91 / 100
  Weights: sw = 0.2123, vcpu = 0.2122, total = 0.4245
  Share in reasonable range.
  Switch deltas: [0, 0, 0, 0, 0]
  Vhost deltas:  [0, 0, 0, 0, 0]
2: <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 1, Cap = 4040.0000 / 4516.1414
  Vhost  Used/Alloc:  CPU = 77 / 79
  Overall: CPU = 77 / 100
  Weights: sw = 0.1750, vcpu = 0.1878, total = 0.3628
  Under-utilized shares: 13. Adjustable shares: 3.
  Switch deltas: [0, 0, 1, 0, 0]
  Vhost deltas:  [0, 0, 2, 0, 0]
0: <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  Switch Used/Alloc:  CPU = 12 / 13, Cap = 2880.0000 / 3994.2975
  Vhost  Used/Alloc:  CPU = 77 / 77
  Overall: CPU = 89 / 100
  Weights: sw = 0.1248, vcpu = 0.1878, total = 0.3126
  Under-utilized shares: 1. Adjustable shares: 1.
  Switch deltas: [0, 0, 1, 1, 0]
  Vhost deltas:  [0, 0, 2, 0, 0]
1: <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 0 / 1, Cap = 3320.0000 / 4516.1414
  Vhost  Used/Alloc:  CPU = 68 / 68
  Overall: CPU = 68 / 100
  Weights: sw = 0.1438, vcpu = 0.1659, total = 0.3097
  Under-utilized shares: 22. Adjustable shares: 0.
  Switch deltas: [0, 0, 1, 1, 1]
  Vhost deltas:  [0, 0, 2, 0, 0]


Assignment 0
  Min cut: 2280
  Machines used:
    <PM #0 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
      CPU: switch_sh=20, vhost={u=40, sh=80}, total={u=45, sh=100}.
    <PM #1 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
      CPU: switch_sh=20, vhost={u=54, sh=80}, total={u=60, sh=100}.
    <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=20, vhost={u=49, sh=80}, total={u=60, sh=100}.
    <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=20, vhost={u=67, sh=80}, total={u=67, sh=100}.
    <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=20, vhost={u=62, sh=80}, total={u=62, sh=100}.
    <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=20, vhost={u=69, sh=80}, total={u=73, sh=100}.
    <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=20, vhost={u=69, sh=80}, total={u=73, sh=100}.
  Machines excluded:
  Assignment of nodes:
    6, 0, 1, 5, 6, 6, 0, 2, 3, 6, 6, 6, 6, 6, 6, 4, 1, 4, 1, 4, 
    1, 4, 2, 4, 4, 4, 4, 2, 2, 3, 3, 2, 2, 2, 2, 0, 2, 2, 3, 3, 
    1, 1, 1, 1, 3, 5, 1, 6, 0, 5, 5, 0, 0, 6, 6, 5, 5, 5, 5, 5, 
    5, 1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 6, 6, 3, 6, 6, 0, 4, 
    4, 4, 5, 5, 3, 1, 5, 5, 6, 3, 1, 5, 5, 0, 3, 1, 1, 4, 4, 4, 
    3, 3, 3, 3, 0, 6, 1, 2, 2, 1, 6, 0, 1, 1, 1, 2, 2, 2, 2, 2, 
    2, 2, 6, 6, 4, 4, 4, 0, 4, 0, 5, 5, 6, 5, 5, 5, 5, 5, 4, 1, 
    1, 3, 4, 4, 3, 3, 3, 3, 6, 2, 2, 1, 5, 1, 2, 2, 2, 2, 2, 2, 
    2, 2, 3, 6, 0, 0, 3, 1, 0, 1, 0, 0, 3, 3, 3, 3, 3, 3, 3, 4, 
    3, 3, 4, 4, 4, 3, 3, 0, 6, 1, 0, 1, 1, 3, 1, 5, 1, 1, 1, 1, 
    0, 1, 1, 0, 2, 3, 2, 2, 2, 3, 2, 2, 0, 4, 3, 3, 3, 3, 3, 3, 
    1, 4, 0, 0, 0, 5, 5, 5, 5, 5, 4, 3, 1, 6, 0, 3, 6, 0, 3, 6, 
    4, 1, 4, 4, 4, 4, 4, 1, 6, 4, 4, 1, 3, 4, 0, 0, 0, 6, 0, 1, 
    0, 3, 2, 5, 5, 2, 5, 4, 5, 5, 5, 5, 0, 3, 6, 3, 3, 3, 3, 4, 
    1, 1, 1, 3, 2, 3, 3, 3, 3, 1, 0, 0, 3, 1, 0, 3, 6, 6, 3, 2, 
    6, 6, 6, 6, 6, 4, 6, 6, 3, 3, 6, 6, 6, 3, 5, 5, 6, 6,

Assignment 1
  Min cut: 1680
  Machines used:
    <PM #1 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
      CPU: switch_sh=20, vhost={u=39, sh=80}, total={u=44, sh=100}.
    <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=20, vhost={u=67, sh=80}, total={u=78, sh=100}.
    <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=20, vhost={u=76, sh=80}, total={u=76, sh=100}.
    <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=20, vhost={u=68, sh=80}, total={u=68, sh=100}.
    <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=20, vhost={u=80, sh=80}, total={u=85, sh=100}.
    <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=20, vhost={u=80, sh=80}, total={u=84, sh=100}.
  Machines excluded:
    <PM #0 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Assignment of nodes:
    6, 1, 2, 5, 6, 6, 1, 3, 6, 6, 5, 6, 6, 6, 6, 4, 3, 4, 2, 4, 
    2, 4, 3, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 6, 1, 
    3, 3, 2, 3, 6, 5, 2, 6, 2, 5, 5, 2, 2, 6, 6, 5, 5, 5, 5, 5, 
    5, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 6, 6, 6, 6, 6, 5, 4, 
    4, 4, 5, 5, 3, 2, 5, 5, 5, 3, 2, 5, 5, 1, 1, 2, 2, 4, 4, 4, 
    1, 1, 1, 6, 1, 6, 3, 3, 3, 2, 6, 1, 2, 2, 2, 3, 3, 3, 3, 3, 
    3, 3, 5, 6, 4, 4, 4, 2, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 4, 2, 
    2, 1, 4, 4, 3, 3, 1, 1, 6, 3, 3, 2, 5, 2, 3, 3, 3, 3, 3, 3, 
    3, 3, 1, 6, 2, 2, 3, 3, 2, 2, 1, 1, 1, 1, 1, 3, 3, 3, 6, 4, 
    3, 3, 4, 4, 4, 6, 6, 2, 6, 2, 1, 2, 2, 1, 2, 5, 2, 2, 2, 2, 
    2, 2, 2, 2, 3, 1, 3, 3, 3, 3, 3, 3, 1, 4, 1, 1, 1, 1, 1, 1, 
    3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 4, 6, 2, 5, 4, 6, 6, 2, 6, 6, 
    4, 2, 4, 4, 4, 4, 4, 2, 6, 4, 4, 2, 1, 4, 6, 6, 6, 6, 2, 2, 
    1, 6, 5, 5, 5, 4, 5, 4, 5, 5, 5, 5, 2, 3, 6, 3, 3, 3, 3, 4, 
    2, 2, 2, 6, 1, 3, 6, 3, 3, 2, 1, 2, 1, 2, 2, 1, 6, 6, 1, 1, 
    6, 6, 6, 6, 6, 4, 6, 6, 6, 1, 6, 6, 6, 1, 5, 5, 6, 6,

Assignment 2
  Min cut: 1240
  Machines used:
    <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=20, vhost={u=71, sh=80}, total={u=82, sh=100}.
    <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=20, vhost={u=78, sh=80}, total={u=78, sh=100}.
    <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=20, vhost={u=73, sh=80}, total={u=73, sh=100}.
    <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=20, vhost={u=94, sh=80}, total={u=98, sh=100}.
    <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=20, vhost={u=94, sh=80}, total={u=100, sh=100}.
  Machines excluded:
    <PM #0 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
    <PM #1 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Assignment of nodes:
    5, 5, 2, 6, 6, 5, 3, 2, 5, 5, 6, 5, 5, 5, 5, 4, 2, 4, 2, 4, 
    2, 4, 3, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 5, 5, 
    2, 2, 2, 2, 5, 6, 2, 5, 3, 6, 6, 2, 2, 5, 5, 6, 6, 6, 6, 6, 
    6, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 5, 5, 5, 5, 6, 5, 
    4, 4, 6, 6, 3, 2, 6, 6, 6, 3, 2, 6, 6, 6, 4, 2, 2, 4, 4, 4, 
    4, 4, 4, 5, 5, 5, 2, 3, 3, 2, 5, 5, 2, 2, 2, 3, 3, 3, 3, 3, 
    3, 3, 6, 5, 4, 4, 4, 2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 
    2, 4, 5, 5, 3, 3, 4, 4, 5, 3, 3, 2, 6, 2, 3, 3, 3, 3, 3, 3, 
    3, 3, 5, 5, 2, 6, 3, 2, 2, 2, 6, 5, 3, 3, 3, 3, 3, 3, 5, 4, 
    3, 3, 4, 4, 5, 5, 5, 2, 5, 2, 5, 2, 2, 3, 2, 6, 2, 2, 2, 3, 
    2, 2, 2, 2, 3, 4, 3, 3, 3, 3, 3, 3, 5, 4, 4, 4, 4, 4, 4, 4, 
    2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 4, 5, 2, 6, 6, 5, 5, 2, 5, 4, 
    4, 2, 4, 4, 4, 4, 4, 2, 6, 4, 5, 3, 3, 4, 5, 5, 5, 5, 2, 2, 
    5, 5, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 2, 3, 6, 3, 3, 3, 3, 5, 
    2, 2, 2, 5, 5, 3, 5, 3, 3, 2, 5, 2, 3, 2, 2, 4, 5, 5, 4, 5, 
    5, 5, 5, 5, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6,

Assignment 3
  Min cut: 940
  Machines used:
    <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=12, vhost={u=75, sh=71}, total={u=87, sh=83}.
    <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=68, sh=80}, total={u=68, sh=81}.
    <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=77, sh=74}, total={u=77, sh=75}.
    <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=4, vhost={u=87, sh=94}, total={u=91, sh=98}.
    <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=6, vhost={u=103, sh=94}, total={u=109, sh=100}.
  Machines excluded:
    <PM #0 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
    <PM #1 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Assignment of nodes:
    5, 5, 2, 6, 6, 5, 2, 2, 4, 6, 6, 5, 5, 5, 5, 4, 2, 4, 2, 4, 
    2, 4, 3, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 4, 4, 
    2, 2, 2, 2, 4, 6, 2, 5, 2, 6, 6, 2, 2, 5, 5, 6, 6, 6, 6, 6, 
    6, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 5, 4, 5, 5, 6, 5, 
    4, 4, 6, 6, 3, 2, 6, 6, 6, 3, 2, 6, 6, 6, 5, 2, 2, 4, 4, 4, 
    5, 5, 5, 4, 5, 5, 2, 3, 3, 2, 5, 5, 2, 2, 2, 3, 3, 3, 3, 3, 
    3, 3, 6, 5, 4, 4, 4, 2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 
    2, 5, 5, 5, 3, 3, 5, 5, 5, 3, 3, 2, 6, 2, 3, 3, 3, 3, 3, 3, 
    3, 3, 4, 5, 2, 6, 3, 2, 2, 2, 6, 5, 6, 6, 6, 3, 3, 3, 4, 4, 
    3, 3, 4, 4, 5, 4, 4, 2, 5, 2, 5, 2, 2, 6, 2, 6, 2, 2, 2, 2, 
    2, 2, 2, 2, 3, 5, 3, 3, 3, 3, 3, 3, 5, 4, 5, 5, 5, 5, 5, 5, 
    2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 4, 4, 2, 6, 6, 4, 5, 2, 4, 5, 
    4, 2, 4, 4, 4, 4, 4, 2, 6, 4, 5, 2, 6, 4, 5, 5, 5, 5, 2, 2, 
    5, 4, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 2, 3, 6, 3, 3, 3, 3, 5, 
    2, 2, 2, 4, 5, 3, 4, 3, 3, 2, 5, 2, 6, 2, 2, 5, 5, 5, 5, 5, 
    5, 5, 5, 5, 5, 4, 5, 5, 4, 4, 5, 5, 5, 4, 6, 6, 6, 6,

Assignment 4
  Min cut: 940
  Machines used:
    <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=13, vhost={u=77, sh=75}, total={u=89, sh=88}.
    <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=68, sh=69}, total={u=68, sh=70}.
    <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=72, sh=79}, total={u=72, sh=80}.
    <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=4, vhost={u=92, sh=87}, total={u=96, sh=91}.
    <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=6, vhost={u=101, sh=100}, total={u=107, sh=106}.
  Machines excluded:
    <PM #0 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
    <PM #1 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Assignment of nodes:
    5, 5, 2, 6, 6, 5, 2, 2, 5, 6, 6, 5, 5, 5, 5, 4, 2, 4, 2, 4, 
    2, 4, 3, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 5, 5, 
    2, 2, 2, 2, 5, 6, 2, 5, 2, 6, 6, 2, 2, 5, 5, 6, 6, 6, 6, 6, 
    6, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 5, 5, 5, 5, 6, 5, 
    4, 4, 6, 6, 3, 2, 6, 6, 6, 3, 2, 6, 6, 6, 4, 2, 2, 4, 4, 4, 
    4, 4, 4, 5, 5, 5, 2, 3, 3, 2, 5, 5, 2, 2, 2, 3, 3, 3, 3, 3, 
    3, 3, 6, 5, 4, 4, 4, 2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 
    2, 4, 5, 5, 3, 3, 4, 4, 5, 3, 3, 2, 6, 2, 3, 3, 3, 3, 3, 3, 
    3, 3, 5, 5, 2, 6, 3, 2, 2, 2, 6, 5, 6, 6, 6, 3, 3, 3, 5, 4, 
    3, 3, 4, 4, 5, 5, 5, 2, 5, 2, 5, 2, 2, 6, 2, 6, 2, 2, 2, 2, 
    2, 2, 2, 2, 3, 4, 3, 3, 3, 3, 3, 3, 5, 4, 4, 4, 4, 4, 4, 4, 
    2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 4, 5, 2, 6, 6, 5, 5, 2, 5, 5, 
    4, 2, 4, 4, 4, 4, 4, 2, 6, 4, 5, 2, 2, 4, 5, 5, 5, 5, 2, 2, 
    5, 5, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 2, 3, 6, 3, 3, 3, 3, 5, 
    2, 2, 2, 5, 5, 3, 5, 3, 3, 2, 5, 2, 2, 2, 2, 4, 5, 5, 4, 5, 
    5, 5, 5, 5, 5, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6,

Assignment 5
  Min cut: 940
  Machines used:
    <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=13, vhost={u=77, sh=77}, total={u=89, sh=90}.
    <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=68, sh=68}, total={u=68, sh=69}.
    <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=77, sh=76}, total={u=77, sh=77}.
    <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=4, vhost={u=87, sh=92}, total={u=91, sh=96}.
    <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=6, vhost={u=101, sh=100}, total={u=107, sh=106}.
  Machines excluded:
    <PM #0 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
    <PM #1 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Assignment of nodes:
    5, 5, 2, 6, 6, 5, 2, 2, 4, 6, 6, 5, 5, 5, 5, 4, 2, 4, 2, 4, 
    2, 4, 3, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 4, 4, 
    2, 2, 2, 2, 4, 6, 2, 5, 2, 6, 6, 2, 2, 5, 5, 6, 6, 6, 6, 6, 
    6, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 5, 4, 5, 5, 6, 5, 
    4, 4, 6, 6, 3, 2, 6, 6, 6, 3, 2, 6, 6, 6, 5, 2, 2, 4, 4, 4, 
    5, 5, 5, 4, 5, 5, 2, 3, 3, 2, 5, 5, 2, 2, 2, 3, 3, 3, 3, 3, 
    3, 3, 6, 5, 4, 4, 4, 2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 
    2, 5, 5, 5, 3, 3, 5, 5, 5, 3, 3, 2, 6, 2, 3, 3, 3, 3, 3, 3, 
    3, 3, 4, 5, 2, 6, 3, 2, 2, 2, 6, 5, 6, 6, 6, 3, 3, 3, 4, 4, 
    3, 3, 4, 4, 5, 4, 4, 2, 5, 2, 5, 2, 2, 6, 2, 6, 2, 2, 2, 2, 
    2, 2, 2, 2, 3, 5, 3, 3, 3, 3, 3, 3, 5, 4, 5, 5, 5, 5, 5, 5, 
    2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 4, 4, 2, 6, 6, 4, 5, 2, 4, 5, 
    4, 2, 4, 4, 4, 4, 4, 2, 6, 4, 5, 2, 2, 4, 5, 5, 5, 5, 2, 2, 
    5, 4, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 2, 3, 6, 3, 3, 3, 3, 5, 
    2, 2, 2, 4, 5, 3, 4, 3, 3, 2, 5, 2, 2, 2, 2, 5, 5, 5, 5, 5, 
    5, 5, 5, 5, 5, 4, 5, 5, 4, 4, 5, 5, 5, 4, 6, 6, 6, 6,

Assignment 6
  Min cut: 940
  Machines used:
    <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=13, vhost={u=77, sh=77}, total={u=89, sh=90}.
    <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=68, sh=68}, total={u=68, sh=69}.
    <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=77, sh=79}, total={u=77, sh=80}.
    <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=4, vhost={u=87, sh=87}, total={u=91, sh=91}.
    <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=6, vhost={u=101, sh=100}, total={u=107, sh=106}.
  Machines excluded:
    <PM #0 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
    <PM #1 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Assignment of nodes:
    5, 5, 2, 6, 6, 5, 2, 2, 4, 6, 6, 5, 5, 5, 5, 4, 2, 4, 2, 4, 
    2, 4, 3, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 4, 4, 
    2, 2, 2, 2, 4, 6, 2, 5, 2, 6, 6, 2, 2, 5, 5, 6, 6, 6, 6, 6, 
    6, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 5, 4, 5, 5, 6, 5, 
    4, 4, 6, 6, 3, 2, 6, 6, 6, 3, 2, 6, 6, 6, 5, 2, 2, 4, 4, 4, 
    5, 5, 5, 4, 5, 5, 2, 3, 3, 2, 5, 5, 2, 2, 2, 3, 3, 3, 3, 3, 
    3, 3, 6, 5, 4, 4, 4, 2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 
    2, 5, 5, 5, 3, 3, 5, 5, 5, 3, 3, 2, 6, 2, 3, 3, 3, 3, 3, 3, 
    3, 3, 4, 5, 2, 6, 3, 2, 2, 2, 6, 5, 6, 6, 6, 3, 3, 3, 4, 4, 
    3, 3, 4, 4, 5, 4, 4, 2, 5, 2, 5, 2, 2, 6, 2, 6, 2, 2, 2, 2, 
    2, 2, 2, 2, 3, 5, 3, 3, 3, 3, 3, 3, 5, 4, 5, 5, 5, 5, 5, 5, 
    2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 4, 4, 2, 6, 6, 4, 5, 2, 4, 5, 
    4, 2, 4, 4, 4, 4, 4, 2, 6, 4, 5, 2, 2, 4, 5, 5, 5, 5, 2, 2, 
    5, 4, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 2, 3, 6, 3, 3, 3, 3, 5, 
    2, 2, 2, 4, 5, 3, 4, 3, 3, 2, 5, 2, 2, 2, 2, 5, 5, 5, 5, 5, 
    5, 5, 5, 5, 5, 4, 5, 5, 4, 4, 5, 5, 5, 4, 6, 6, 6, 6,

Best assignment out of 7 candidates is...

Assignment 3
  Min cut: 940
  Machines used:
    <PM #2 | (8, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=12, vhost={u=75, sh=71}, total={u=87, sh=83}.
    <PM #3 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=68, sh=80}, total={u=68, sh=81}.
    <PM #4 | (0, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=1, vhost={u=77, sh=74}, total={u=77, sh=75}.
    <PM #5 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=4, vhost={u=87, sh=94}, total={u=91, sh=98}.
    <PM #6 | (0, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=6, vhost={u=103, sh=94}, total={u=109, sh=100}.
  Machines excluded:
    <PM #0 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
    <PM #1 | (1, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Assignment of nodes:
    5, 5, 2, 6, 6, 5, 2, 2, 4, 6, 6, 5, 5, 5, 5, 4, 2, 4, 2, 4, 
    2, 4, 3, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 2, 3, 3, 4, 4, 
    2, 2, 2, 2, 4, 6, 2, 5, 2, 6, 6, 2, 2, 5, 5, 6, 6, 6, 6, 6, 
    6, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 5, 5, 4, 5, 5, 6, 5, 
    4, 4, 6, 6, 3, 2, 6, 6, 6, 3, 2, 6, 6, 6, 5, 2, 2, 4, 4, 4, 
    5, 5, 5, 4, 5, 5, 2, 3, 3, 2, 5, 5, 2, 2, 2, 3, 3, 3, 3, 3, 
    3, 3, 6, 5, 4, 4, 4, 2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 6, 4, 2, 
    2, 5, 5, 5, 3, 3, 5, 5, 5, 3, 3, 2, 6, 2, 3, 3, 3, 3, 3, 3, 
    3, 3, 4, 5, 2, 6, 3, 2, 2, 2, 6, 5, 6, 6, 6, 3, 3, 3, 4, 4, 
    3, 3, 4, 4, 5, 4, 4, 2, 5, 2, 5, 2, 2, 6, 2, 6, 2, 2, 2, 2, 
    2, 2, 2, 2, 3, 5, 3, 3, 3, 3, 3, 3, 5, 4, 5, 5, 5, 5, 5, 5, 
    2, 4, 6, 6, 6, 6, 6, 6, 6, 6, 4, 4, 2, 6, 6, 4, 5, 2, 4, 5, 
    4, 2, 4, 4, 4, 4, 4, 2, 6, 4, 5, 2, 6, 4, 5, 5, 5, 5, 2, 2, 
    5, 4, 6, 6, 6, 6, 6, 4, 6, 6, 6, 6, 2, 3, 6, 3, 3, 3, 3, 5, 
    2, 2, 2, 4, 5, 3, 4, 3, 3, 2, 5, 2, 6, 2, 2, 5, 5, 5, 5, 5, 
    5, 5, 5, 5, 5, 4, 5, 5, 4, 4, 5, 5, 5, 4, 6, 6, 6, 6,

```
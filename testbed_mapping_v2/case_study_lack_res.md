# Case Study: When Resource is Not Enough

```
xb@ubuntu:[~/Desktop/cs590-map/testbed_mapping_v2]: ./main.py -g input/1221.r0.cch.abr.graph -p input/pms_from_paper_4.txt -c input/1221_410.host

Namespace(graph_file='input/1221.r0.cch.abr.graph', pm_file='input/pms_from_paper_4.txt', vhost_cpu_file='input/1221_410.host')

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

Read 4 PMs from input:
  <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>

********************************************************************************
********************************  Assignment 0  ********************************
********************************************************************************

sw_cpu_shares: [20, 20, 20, 20]
sw_cap_shares: [7457.4763, 9132.043400000002, 15343.1926, 28075.7285]
vh_cpu_shares: [80, 80, 80, 80]
min_cut:       1380

PM Elimination Phase:
  Target PM: #0, sticky=False
  Total free CPU shares: -66
  Shares covered by PM:  87
  No PM can be excluded from next round.

Share Adjustment Phase:
3: <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 10 / 20, Cap = 10140.0000 / 28075.7285
  Vhost  Used/Alloc:  CPU = 117 / 80
  Overall: CPU = 127 / 100
  Weights: sw = 0.4393, vcpu = 0.2854, total = 0.7247
  Over by 27 shares. Dispose 27 shares to the next PM.
  Switch deltas: [0, 2, 0, 0]
  Vhost deltas:  [-27, 25, 0, 0]
2: <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 10 / 20, Cap = 6410.0000 / 15343.1926
  Vhost  Used/Alloc:  CPU = 117 / 80
  Overall: CPU = 127 / 100
  Weights: sw = 0.2777, vcpu = 0.2854, total = 0.5631
  Over by 54 shares. Dispose 54 shares to the next PM.
  Switch deltas: [0, 0, 6, 0]
  Vhost deltas:  [-27, -27, 48, 0]
1: <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  Switch Used/Alloc:  CPU = 13 / 20, Cap = 3820.0000 / 9132.0434
  Vhost  Used/Alloc:  CPU = 99 / 80
  Overall: CPU = 112 / 100
  Weights: sw = 0.1655, vcpu = 0.2415, total = 0.4070
  Over by 66 shares. Dispose 66 shares to the next PM.
  Switch deltas: [0, 0, -1, 7]
  Vhost deltas:  [-27, -27, -11, 59]
0: <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Switch Used/Alloc:  CPU = 10 / 20, Cap = 2710.0000 / 7457.4763
  Vhost  Used/Alloc:  CPU = 77 / 80
  Overall: CPU = 87 / 100
  Weights: sw = 0.1174, vcpu = 0.1878, total = 0.3052
  Over by 53 shares. No other PM can take it.
  Switch deltas: [0, 0, -1, 7]
  Vhost deltas:  [-27, -27, -11, 59]


********************************************************************************
********************************  Assignment 1  ********************************
********************************************************************************

sw_cpu_shares: [17, 12, 10, 10]
sw_cap_shares: [6281.2759, 3260.3337999999994, 9127.2626, 14066.1505]
vh_cpu_shares: [100, 88, 90, 90]
min_cut:       1000

PM Elimination Phase:
  Target PM: #1, sticky=False
  Total free CPU shares: -61
  Shares covered by PM:  94
  No PM can be excluded from next round.

Share Adjustment Phase:
3: <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 10 / 10, Cap = 8700.0000 / 14066.1505
  Vhost  Used/Alloc:  CPU = 116 / 90
  Overall: CPU = 126 / 100
  Weights: sw = 0.3769, vcpu = 0.2829, total = 0.6599
  Over by 26 shares. Dispose 26 shares to the next PM.
  Switch deltas: [0, 2, 0, 0]
  Vhost deltas:  [-26, 24, 0, 0]
2: <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 10 / 10, Cap = 7080.0000 / 9127.2626
  Vhost  Used/Alloc:  CPU = 106 / 90
  Overall: CPU = 116 / 100
  Weights: sw = 0.3068, vcpu = 0.2585, total = 0.5653
  Over by 42 shares. Dispose 42 shares to the next PM.
  Switch deltas: [0, 0, 4, 0]
  Vhost deltas:  [-26, -16, 38, 0]
0: <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Switch Used/Alloc:  CPU = 14 / 17, Cap = 4870.0000 / 6281.2759
  Vhost  Used/Alloc:  CPU = 105 / 100
  Overall: CPU = 119 / 100
  Weights: sw = 0.2110, vcpu = 0.2561, total = 0.4671
  Over by 61 shares. Dispose 61 shares to the next PM.
  Switch deltas: [0, 0, -3, 7]
  Vhost deltas:  [-26, -16, -16, 54]
1: <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  Switch Used/Alloc:  CPU = 11 / 12, Cap = 2430.0000 / 3260.3338
  Vhost  Used/Alloc:  CPU = 83 / 88
  Overall: CPU = 94 / 100
  Weights: sw = 0.1053, vcpu = 0.2024, total = 0.3077
  Over by 55 shares. No other PM can take it.
  Switch deltas: [0, 0, -3, 7]
  Vhost deltas:  [-26, -16, -16, 54]


********************************************************************************
********************************  Assignment 2  ********************************
********************************************************************************

sw_cpu_shares: [11, 18, 10, 10]
sw_cap_shares: [3928.8751, 7664.116000000001, 9127.2626, 14066.1505]
vh_cpu_shares: [89, 100, 90, 90]
min_cut:       900

PM Elimination Phase:
  Target PM: #0, sticky=False
  Total free CPU shares: -67
  Shares covered by PM:  88
  No PM can be excluded from next round.

Share Adjustment Phase:
3: <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 10 / 10, Cap = 8510.0000 / 14066.1505
  Vhost  Used/Alloc:  CPU = 115 / 90
  Overall: CPU = 125 / 100
  Weights: sw = 0.3687, vcpu = 0.2805, total = 0.6492
  Over by 25 shares. Dispose 25 shares to the next PM.
  Switch deltas: [0, 2, 0, 0]
  Vhost deltas:  [-25, 23, 0, 0]
2: <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 10 / 10, Cap = 6580.0000 / 9127.2626
  Vhost  Used/Alloc:  CPU = 108 / 90
  Overall: CPU = 118 / 100
  Weights: sw = 0.2851, vcpu = 0.2634, total = 0.5485
  Over by 43 shares. Dispose 43 shares to the next PM.
  Switch deltas: [0, 0, 5, 0]
  Vhost deltas:  [-25, -18, 38, 0]
1: <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  Switch Used/Alloc:  CPU = 15 / 18, Cap = 5370.0000 / 7664.1160
  Vhost  Used/Alloc:  CPU = 109 / 100
  Overall: CPU = 124 / 100
  Weights: sw = 0.2327, vcpu = 0.2659, total = 0.4985
  Over by 67 shares. Dispose 67 shares to the next PM.
  Switch deltas: [0, 0, -3, 7]
  Vhost deltas:  [-25, -18, -21, 60]
0: <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Switch Used/Alloc:  CPU = 10 / 11, Cap = 2620.0000 / 3928.8751
  Vhost  Used/Alloc:  CPU = 78 / 89
  Overall: CPU = 88 / 100
  Weights: sw = 0.1135, vcpu = 0.1902, total = 0.3038
  Over by 55 shares. No other PM can take it.
  Switch deltas: [0, 0, -3, 7]
  Vhost deltas:  [-25, -18, -21, 60]


********************************************************************************
********************************  Assignment 3  ********************************
********************************************************************************

sw_cpu_shares: [17, 12, 10, 10]
sw_cap_shares: [6281.2759, 3260.3337999999994, 9127.2626, 14066.1505]
vh_cpu_shares: [100, 88, 90, 90]
min_cut:       1000

PM Elimination Phase:
  Target PM: #1, sticky=False
  Total free CPU shares: -61
  Shares covered by PM:  94
  No PM can be excluded from next round.

Share Adjustment Phase:
3: <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
  Switch Used/Alloc:  CPU = 10 / 10, Cap = 8700.0000 / 14066.1505
  Vhost  Used/Alloc:  CPU = 116 / 90
  Overall: CPU = 126 / 100
  Weights: sw = 0.3769, vcpu = 0.2829, total = 0.6599
  Over by 26 shares. Dispose 26 shares to the next PM.
  Switch deltas: [0, 2, 0, 0]
  Vhost deltas:  [-26, 24, 0, 0]
2: <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
  Switch Used/Alloc:  CPU = 10 / 10, Cap = 7080.0000 / 9127.2626
  Vhost  Used/Alloc:  CPU = 106 / 90
  Overall: CPU = 116 / 100
  Weights: sw = 0.3068, vcpu = 0.2585, total = 0.5653
  Over by 42 shares. Dispose 42 shares to the next PM.
  Switch deltas: [0, 0, 4, 0]
  Vhost deltas:  [-26, -16, 38, 0]
0: <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
  Switch Used/Alloc:  CPU = 14 / 17, Cap = 4870.0000 / 6281.2759
  Vhost  Used/Alloc:  CPU = 105 / 100
  Overall: CPU = 119 / 100
  Weights: sw = 0.2110, vcpu = 0.2561, total = 0.4671
  Over by 61 shares. Dispose 61 shares to the next PM.
  Switch deltas: [0, 0, -3, 7]
  Vhost deltas:  [-26, -16, -16, 54]
1: <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
  Switch Used/Alloc:  CPU = 11 / 12, Cap = 2430.0000 / 3260.3338
  Vhost  Used/Alloc:  CPU = 83 / 88
  Overall: CPU = 94 / 100
  Weights: sw = 0.1053, vcpu = 0.2024, total = 0.3077
  Over by 55 shares. No other PM can take it.
  Switch deltas: [0, 0, -3, 7]
  Vhost deltas:  [-26, -16, -16, 54]


Assignment 0
  Min cut: 1380
  Machines used:
    <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
      CPU: switch_sh=20, vhost={u=77, sh=80}, total={u=87, sh=100}.
    <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=20, vhost={u=99, sh=80}, total={u=112, sh=100}.
    <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=20, vhost={u=117, sh=80}, total={u=127, sh=100}.
    <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=20, vhost={u=117, sh=80}, total={u=127, sh=100}.
  Machines excluded:
  Assignment of nodes:
    2, 1, 0, 3, 3, 1, 0, 1, 2, 3, 3, 3, 3, 2, 2, 2, 1, 2, 0, 2, 
    0, 2, 1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 1, 1, 0, 1, 1, 2, 2, 
    1, 1, 0, 1, 2, 3, 0, 3, 0, 3, 3, 0, 0, 3, 2, 3, 3, 3, 3, 3, 
    3, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 1, 1, 0, 2, 
    2, 2, 3, 3, 2, 0, 3, 3, 3, 2, 0, 3, 3, 0, 1, 0, 0, 2, 2, 2, 
    1, 1, 1, 2, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 
    1, 1, 3, 3, 2, 2, 2, 0, 2, 1, 3, 3, 3, 3, 3, 3, 3, 3, 2, 0, 
    0, 1, 2, 2, 2, 2, 1, 1, 3, 1, 1, 0, 3, 0, 1, 1, 1, 1, 1, 1, 
    1, 1, 2, 2, 0, 0, 2, 1, 0, 0, 1, 2, 0, 0, 0, 2, 2, 2, 2, 2, 
    2, 2, 2, 2, 2, 2, 2, 0, 3, 0, 1, 0, 0, 0, 0, 3, 0, 0, 0, 0, 
    0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 
    1, 2, 1, 1, 1, 3, 3, 3, 3, 3, 2, 2, 0, 3, 1, 2, 1, 0, 2, 1, 
    2, 0, 2, 2, 2, 2, 2, 0, 3, 2, 2, 0, 0, 2, 1, 1, 1, 3, 0, 0, 
    1, 2, 0, 3, 3, 1, 3, 2, 3, 3, 3, 3, 0, 2, 3, 2, 2, 2, 2, 2, 
    0, 0, 0, 2, 2, 2, 2, 2, 2, 0, 1, 0, 0, 0, 0, 1, 3, 3, 1, 1, 
    2, 3, 3, 3, 3, 2, 3, 3, 2, 2, 3, 1, 1, 2, 3, 3, 3, 3,

Assignment 1
  Min cut: 1000
  Machines used:
    <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
      CPU: switch_sh=17, vhost={u=105, sh=100}, total={u=119, sh=117}.
    <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=12, vhost={u=83, sh=88}, total={u=94, sh=100}.
    <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=10, vhost={u=106, sh=90}, total={u=116, sh=100}.
    <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=10, vhost={u=116, sh=90}, total={u=126, sh=100}.
  Machines excluded:
  Assignment of nodes:
    1, 1, 1, 3, 3, 3, 0, 1, 2, 3, 3, 2, 2, 2, 2, 2, 1, 2, 1, 2, 
    1, 2, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 
    1, 1, 1, 1, 2, 3, 1, 2, 1, 3, 3, 0, 0, 2, 2, 3, 3, 3, 3, 3, 
    3, 1, 2, 2, 2, 1, 2, 2, 1, 1, 1, 2, 0, 3, 3, 2, 3, 3, 3, 2, 
    2, 1, 3, 3, 0, 1, 3, 3, 3, 0, 1, 3, 3, 1, 0, 1, 1, 2, 2, 2, 
    0, 0, 0, 2, 1, 3, 1, 0, 0, 1, 3, 1, 1, 1, 1, 0, 0, 0, 0, 0, 
    0, 0, 3, 2, 2, 2, 2, 0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1, 
    1, 0, 2, 2, 0, 0, 0, 0, 2, 0, 0, 1, 3, 1, 0, 0, 0, 0, 0, 0, 
    0, 0, 1, 2, 0, 0, 0, 1, 0, 1, 3, 1, 3, 3, 3, 0, 0, 0, 2, 2, 
    0, 0, 2, 2, 2, 2, 2, 0, 2, 1, 1, 1, 1, 3, 1, 3, 1, 1, 1, 1, 
    0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 
    1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 1, 3, 3, 2, 3, 0, 2, 3, 
    2, 1, 1, 1, 2, 2, 1, 1, 3, 2, 2, 1, 3, 2, 3, 3, 3, 2, 0, 1, 
    1, 2, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 0, 0, 3, 0, 0, 0, 0, 2, 
    1, 1, 1, 2, 1, 0, 2, 0, 0, 1, 1, 0, 0, 1, 0, 0, 2, 2, 0, 1, 
    2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 3, 3, 1, 3, 3, 3, 3,

Assignment 2
  Min cut: 900
  Machines used:
    <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
      CPU: switch_sh=11, vhost={u=78, sh=89}, total={u=88, sh=100}.
    <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=18, vhost={u=109, sh=100}, total={u=124, sh=118}.
    <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=10, vhost={u=108, sh=90}, total={u=118, sh=100}.
    <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=10, vhost={u=115, sh=90}, total={u=125, sh=100}.
  Machines excluded:
  Assignment of nodes:
    2, 0, 0, 3, 3, 3, 1, 0, 1, 3, 3, 2, 2, 2, 2, 2, 0, 2, 0, 2, 
    0, 2, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 
    0, 0, 0, 0, 1, 3, 0, 2, 1, 3, 3, 0, 0, 2, 2, 3, 3, 3, 3, 3, 
    3, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 3, 3, 1, 3, 3, 3, 2, 
    2, 2, 3, 3, 1, 0, 3, 3, 3, 1, 0, 3, 3, 3, 1, 0, 0, 2, 2, 2, 
    1, 1, 1, 1, 2, 3, 0, 1, 1, 0, 3, 0, 0, 0, 0, 1, 1, 1, 1, 1, 
    1, 1, 2, 2, 2, 2, 2, 0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 0, 
    0, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1, 0, 3, 0, 1, 1, 1, 1, 1, 1, 
    1, 1, 1, 2, 0, 0, 1, 0, 0, 0, 3, 2, 3, 3, 3, 1, 1, 1, 1, 2, 
    1, 1, 2, 2, 2, 1, 1, 0, 2, 0, 0, 0, 0, 3, 0, 3, 0, 0, 0, 0, 
    0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 1, 1, 1, 1, 1, 1, 
    0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1, 0, 3, 3, 1, 3, 0, 1, 3, 
    2, 0, 2, 2, 2, 2, 2, 0, 3, 2, 2, 0, 1, 2, 3, 3, 3, 2, 0, 0, 
    2, 1, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 0, 1, 3, 1, 1, 1, 1, 2, 
    0, 0, 0, 1, 2, 1, 1, 1, 1, 0, 2, 0, 1, 0, 0, 1, 2, 2, 1, 2, 
    2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 3, 3, 1, 3, 3, 3, 3,

Assignment 3
  Min cut: 1000
  Machines used:
    <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
      CPU: switch_sh=17, vhost={u=105, sh=100}, total={u=119, sh=117}.
    <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=12, vhost={u=83, sh=88}, total={u=94, sh=100}.
    <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=10, vhost={u=106, sh=90}, total={u=116, sh=100}.
    <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=10, vhost={u=116, sh=90}, total={u=126, sh=100}.
  Machines excluded:
  Assignment of nodes:
    1, 1, 1, 3, 3, 3, 0, 1, 2, 3, 3, 2, 2, 2, 2, 2, 1, 2, 1, 2, 
    1, 2, 0, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 
    1, 1, 1, 1, 2, 3, 1, 2, 1, 3, 3, 0, 0, 2, 2, 3, 3, 3, 3, 3, 
    3, 1, 2, 2, 2, 1, 2, 2, 1, 1, 1, 2, 0, 3, 3, 2, 3, 3, 3, 2, 
    2, 1, 3, 3, 0, 1, 3, 3, 3, 0, 1, 3, 3, 1, 0, 1, 1, 2, 2, 2, 
    0, 0, 0, 2, 1, 3, 1, 0, 0, 1, 3, 1, 1, 1, 1, 0, 0, 0, 0, 0, 
    0, 0, 3, 2, 2, 2, 2, 0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1, 
    1, 0, 2, 2, 0, 0, 0, 0, 2, 0, 0, 1, 3, 1, 0, 0, 0, 0, 0, 0, 
    0, 0, 1, 2, 0, 0, 0, 1, 0, 1, 3, 1, 3, 3, 3, 0, 0, 0, 2, 2, 
    0, 0, 2, 2, 2, 2, 2, 0, 2, 1, 1, 1, 1, 3, 1, 3, 1, 1, 1, 1, 
    0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 
    1, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 1, 3, 3, 2, 3, 0, 2, 3, 
    2, 1, 1, 1, 2, 2, 1, 1, 3, 2, 2, 1, 3, 2, 3, 3, 3, 2, 0, 1, 
    1, 2, 3, 3, 3, 3, 3, 1, 3, 3, 3, 3, 0, 0, 3, 0, 0, 0, 0, 2, 
    1, 1, 1, 2, 1, 0, 2, 0, 0, 1, 1, 0, 0, 1, 0, 0, 2, 2, 0, 1, 
    2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 3, 3, 1, 3, 3, 3, 3,

Best assignment out of 4 candidates is...

Assignment 2
  Min cut: 900
  Machines used:
    <PM #0 | (10, 100)/100 | f(u) = 0.0000 u^2 + 392.0668 u^1 + -383.8597 u^0>
      CPU: switch_sh=11, vhost={u=78, sh=89}, total={u=88, sh=100}.
    <PM #1 | (10, 100)/100 | f(u) = 0.0000 u^2 + 733.9637 u^1 + -5547.2306 u^0>
      CPU: switch_sh=18, vhost={u=109, sh=100}, total={u=124, sh=118}.
    <PM #2 | (10, 100)/100 | f(u) = 5.7498 u^2 + 449.0990 u^1 + 4061.2926 u^0>
      CPU: switch_sh=10, vhost={u=108, sh=90}, total={u=118, sh=100}.
    <PM #3 | (10, 100)/100 | f(u) = 4.4591 u^2 + 1267.1848 u^1 + 948.3925 u^0>
      CPU: switch_sh=10, vhost={u=115, sh=90}, total={u=125, sh=100}.
  Machines excluded:
  Assignment of nodes:
    2, 0, 0, 3, 3, 3, 1, 0, 1, 3, 3, 2, 2, 2, 2, 2, 0, 2, 0, 2, 
    0, 2, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 
    0, 0, 0, 0, 1, 3, 0, 2, 1, 3, 3, 0, 0, 2, 2, 3, 3, 3, 3, 3, 
    3, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 3, 3, 1, 3, 3, 3, 2, 
    2, 2, 3, 3, 1, 0, 3, 3, 3, 1, 0, 3, 3, 3, 1, 0, 0, 2, 2, 2, 
    1, 1, 1, 1, 2, 3, 0, 1, 1, 0, 3, 0, 0, 0, 0, 1, 1, 1, 1, 1, 
    1, 1, 2, 2, 2, 2, 2, 0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 0, 
    0, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1, 0, 3, 0, 1, 1, 1, 1, 1, 1, 
    1, 1, 1, 2, 0, 0, 1, 0, 0, 0, 3, 2, 3, 3, 3, 1, 1, 1, 1, 2, 
    1, 1, 2, 2, 2, 1, 1, 0, 2, 0, 0, 0, 0, 3, 0, 3, 0, 0, 0, 0, 
    0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 1, 1, 1, 1, 1, 1, 
    0, 2, 3, 3, 3, 3, 3, 3, 3, 3, 2, 1, 0, 3, 3, 1, 3, 0, 1, 3, 
    2, 0, 2, 2, 2, 2, 2, 0, 3, 2, 2, 0, 1, 2, 3, 3, 3, 2, 0, 0, 
    2, 1, 3, 3, 3, 3, 3, 2, 3, 3, 3, 3, 0, 1, 3, 1, 1, 1, 1, 2, 
    0, 0, 0, 1, 2, 1, 1, 1, 1, 0, 2, 0, 1, 0, 0, 1, 2, 2, 1, 2, 
    2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 3, 3, 1, 3, 3, 3, 3,
```
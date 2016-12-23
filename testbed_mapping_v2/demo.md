# Examples

## PM Information
We artificially scaled the four capacity functions we presented in section III.A to simulate six PMs in order to guarantee the total capacity is large enough for all example topologies. Details of the six PMs are listed as follows:
  
  
| PM  | Max | MinPP | MaxPP | Capacity Function |
|:---:|:---:|:-----:|:-----:|:-----------------:|
| PM1 | 390 |   0   | 360   | 2.79u^2 + 3167.96u + 9483.93 |
| PM2 | 390 |   0   | 360   | 2.79u^2 + 3167.96u + 9483.93 |
| PM3 | 390 |   0   | 360   | 3.59u^2 + 1122.75u + 40612.92 |
| PM4 | 190 |   0   | 180   | 4.25u^2 + 2851.66u - 27096.99 |
| PM5 | 190 |   0   | 180   | 4.25u^2 + 2851.66u - 27096.99 |
| PM6 | 190 |   0   | 180   | 0.168u^2 + 1929.44u - 2868.28 |

##RocketFuel Topology
The [RocketFuel topology](cs590-map/testbed_mapping_v2/icdcs2017/rocketfuel-318sw/rocketfuel-318sw.graph)  we use includes  `318` vertices and `758` edges. The total vertex weight is `18625` and total edge weight is `7580`. The CPU share requirements we assign to [end hosts](cs590-map/testbed_mapping_v2/icdcs2017/rocketfuel-318sw/rocketfuel-318sw.host) sum up to `693`.

CPU usage of `PM_i` is presented as `(host_u_i + pp_u_i)/Max_i`, where `(host_u_i + pp_u_i)` is the total CPU usage for end hosts and switches.
| Algorithm | Edge-cut | PM1 | PM2 | PM3 | PM4 | PM5 | PM6 |
|:---------:|:--------:|:---:|:---:|:---:|:---:|:---:|:---:|
|Equal-METIS| 1350 | 200/390 | 148/390 | 243/390 | 235/190 | 262/190 | 285/190 |
|C_i(0.9)   | 380  | 378/390 | 300/390 | 224/390 | 164/190 | 145/190 | 89/190  |
|Waterfall  | 240  | 397/390 | 389/390 | 391/390 |   N/A   |   N/A   | 132/190 |

Visualization of partitioning results for __Equal-METIS__:
![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/icdcs2017/rocketfuel-318sw/baseline/assignment_BALANCED_6PMs.svg)

Visualization of partitioning results for __C_i(0.9)__:
![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/icdcs2017/rocketfuel-318sw/baseline/assignment_C90_CAPACITY_6PMs.svg)

Visualization of partitioning results for __Waterfall__:
![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/icdcs2017/rocketfuel-318sw/waterfall/assignment_best.svg)


### Jellyfish Topology

The [Jellyfish topology](cs590-map/testbed_mapping_v2/icdcs2017/jellyfish-320sw/jellyfish-320sw.graph) we use includes  `320` vertices and `960` edges. The total vertex weight is `20800` and total edge weight is `9600`. The CPU share requirements we assign to [end hosts](cs590-map/testbed_mapping_v2/icdcs2017/jellyfish-320sw/jellyfish-320sw.host) sum up to `480`.

| Algorithm | Edge-cut | PM1 | PM2 | PM3 | PM4 | PM5 | PM6 |
|:---------:|:--------:|:---:|:---:|:---:|:---:|:---:|:---:|
|Equal-METIS| 4150 | 183/390 | 172/390 | 249/390 | 186/190 | 190/190 | 253/190 |
|C_i(0.9)   | 4010 | 291/390 | 336/390 | 224/390 | 110/190 | 116/190 | 67/190  |
|Waterfall  | 2980 | 389/390 | 392/390 | 323/390 |    NA   |   NA   |   NA   |

Visualization of partitioning results for __Equal-METIS__:
![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/icdcs2017/jellyfish-320sw/baseline/assignment_BALANCED_6PMs.svg)

Visualization of partitioning results for __C_i(0.9)__:
![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/icdcs2017/jellyfish-320sw/baseline/assignment_C90_CAPACITY_6PMs.svg)

Visualization of partitioning results for __Waterfall__:
![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/icdcs2017/jellyfish-320sw/waterfall/assignment_best.svg)


### Fat-tree Topology
The [Fat-tree topology](cs590-map/testbed_mapping_v2/icdcs2017/fattree-320sw/fattree-320sw.graph) we use includes  `320` vertices and `2048` edges. The total vertex weight is `42240` and total edge weight is `20480`. The CPU share requirements we assign to [end hosts](cs590-map/testbed_mapping_v2/icdcs2017/fattree-320sw/fattree-320sw.host) sum up to `384`.

| Algorithm | Edge-cut | PM1 | PM2 | PM3 | PM4 | PM5 | PM6 |
|:---------:|:--------:|:---:|:---:|:---:|:---:|:---:|:---:|
|Equal-METIS| 8480 | 256/390 | 256/390 | 337/390 | 266/190 | 237/190 | 419/190 |
|C_i(0.9)   | 9120 | 197/390 | 225/390 | 160/390 | 462/190 | 326/190 | 78/190  |
|Waterfall  | 9030 | 389/390 | 389/390 | 390/390 | 166/190 | 190/190 | 105/190 |

Visualization of partitioning results for __Equal-METIS__:
![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/icdcs2017/fattree-320sw/baseline/assignment_BALANCED_6PMs.svg)

Visualization of partitioning results for __C_i(0.9)__:
![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/icdcs2017/fattree-320sw/baseline/assignment_C90_CAPACITY_6PMs.svg)

Visualization of partitioning results for __Waterfall__:
![](https://rawgithub.com/xybu/cs590-map/master/testbed_mapping_v2/icdcs2017/fattree-320sw/waterfall/assignment_best.svg)



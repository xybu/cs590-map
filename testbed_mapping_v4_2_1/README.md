Testbed Mapping
===============

This is the proof-of-concept implementation of our idea presented in our paper about high fidelity testbed mapping. More details, demos, and experiments can be found in [the paper](https://www.cs.purdue.edu/homes/fahmy/papers/high-fidelity-network.pdf) and
[presentation slides](https://www.cs.purdue.edu/homes/fahmy/talks/icccn2017.pdf).

## Usage

```
xb@ubuntu:[~/Desktop/cs590-map/testbed_mapping_v4_2_1]: ./main.py --help
usage: main.py [-h] -g GRAPH_FILE -p PM_FILE -c VHOST_CPU_FILE [-o OUT]
               [--sw-imbalance-factor SW_IMBALANCE_FACTOR]
               [--vhost-imbalance-factor VHOST_IMBALANCE_FACTOR] [--find-iv]

A refined graph partition algorithm based on METIS.

optional arguments:
  -h, --help            show this help message and exit
  -g GRAPH_FILE, --graph-file GRAPH_FILE
                        File to read input graph from.
  -p PM_FILE, --pm-file PM_FILE
                        File to read PM information.
  -c VHOST_CPU_FILE, --vhost-cpu-file VHOST_CPU_FILE
                        File to read vhost CPU information.
  -o OUT, --out OUT     If given, will generate output files to this dir.
  --sw-imbalance-factor SW_IMBALANCE_FACTOR
                        Imbalance factor for switch constraint. Use a value in
                        [0, 0.15].
  --vhost-imbalance-factor VHOST_IMBALANCE_FACTOR
                        Imbalance factor for vhost CPU constraint. Use a value
                        in [0, 0.15].
  --find-iv, --find-imbalance-vector
                        If set, brute force potentially best imbalance vector.
```

For example,

```
./main.py -g input/graphs/1221.r0.cch.abr.graph -c input/graphs/1221_1053rnd.host -p input/pm/pms_01230123.txt --find-iv
```

More sample graphs and corresponding virtual host CPU requirement files, and definitions of physical machines (PMs), can be found
in the `input/` directory.

## File Hierarchy

* `demo/`: some interesting test cases we found along the way, and scripts to produce new results.
* `doc/`: some questions we discussed during the meetings, and their potential solutions.
* `input/`: input graphs, vhost CPU requirement files, and PM definitions.
* `constants.py`: where all the program-wide constants are defined.
* `gen_baseline.py`: the script to generate baseline results using the same input.
* `main.py`: the main program of our implementation.
* `metis.py`: Python binding of METIS library.
* `models.py`: abstractions of capacity function, physical machine, etc., are defined here.
* `requirements.txt`: packages this program depends on.
* `utils_input.py`: utility functions used for processing input by both `gen_baseline.py` and `main.py`.

## Installation

Assuming Ubuntu 16.04:

```bash
sudo apt install python3-tk libcgraph6 graphviz-dev graphviz python-dev python3-dev
wget -O- https://bootstrap.pypa.io/get-pip.py | sudo python3
pip3 install -r requirements.txt

# Install METIS from source.
cd /tmp
wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz
tar xvf metis-5.1.0.tar.gz
cd metis-5.1.0
make config shared=1
make -j`nproc`
sudo make install
sudo ldconfig
```

## ChangeLog

### From v4_1

1. Can move shares upwards as well.

2. More aggressive moving avg value and conservative over threshold.

There are a few ways to reduce the gap between prev input and next input:

(1). Set imb vec to [0.01, 0.01] of subsequent shares of each branch in share adjustment phase -- but METIS gives bad result.
(2). Use a moving average for prev and next (derived) input -- adopted by this version.
(3). Derive next input from prev input, rather than basing next input on result of prev input -- to be tried in v5.

### From v3

Compared to v3, the branching strategy of v4 is to include more PMs as needed, instead of eliminating PMs.

This step is to find out the smallest set of PMs needed so that branching step only extends the set. To obtain the
smallest possible (lowerbound) set, for each resource we estimate scarcity by max possible available and min
possible need.

For CPU share resource the max possible each PM can offer is its MAX_CPU_SHARE value. The minimum possible need is
the sum of vhost CPU requirements. Actual need is at least this value because of need for packet switching.

For switching capacity resource the max possible each PM can offer is the capacity at the PM's MAX_SWITCH_CPU_SHARE.
The minimum possible and actual need is the sum of vertex weights in the graph.

If more constraints are to added, the same logic applies.

The problem is stated as follows:

```
Objective:
    Min number of PMs chosen

Constraints:
    For each resource R_i,
        sum(max possible offering for R_i by each PM) >= min need for R_i
```

A greedy approach based on assumption that need for one particular resource usually dominates need for all other
resources.

1. Sort the resource constraints from most to least scarce (i.e., in ascending order of sum of max available from each PM / min_need).
   Let the sorted resource constraints be Ra, Rb, ..., Rs.

2. Use each PM's max possible offerings for each of resources Ra, Rb, ..., Rs, as keys and sort the PMs in descending order.
   Let the sorted PM list be PM1, PM2, ..., PMk.

3. Starting from empty set {}, iteratively put PM1, PM2, ..., PMk' to the set until for all resources the max possible
   offering for the resource by all PMs in the set is at least the min possible need for that resource. 

## Evaulation of Changes

When resource is abundant, the program runs significantly faster.

When switching resource is similarly scarce as vhost CPU resource, the algorithm gives bad estimate
(cap_f(MAX_SWITCH_CPU_SHARE) is too optimistic because PMs can't use that much CPU shares for packet switching).
In this case the program runs slower.

Patch: if a new branch is created because all PMs are stressed, then in share adjustment phase slash the counter -- did.

The range of iv brute force is shrinked because the resource bound is usually tight.

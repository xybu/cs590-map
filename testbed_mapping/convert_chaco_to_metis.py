#!/usr/bin/python3

import sys

import metis

import oracles
import parse_input

chaco_graph_file = sys.argv[1]
vhost_cpu_file = sys.argv[2]
oracle = oracles.ChacoOracle(chaco_graph_file)
oracle.update_vhost_cpu_req(parse_input.read_flat_ints(vhost_cpu_file))

metis.networkx_to_metis(oracle.graph)

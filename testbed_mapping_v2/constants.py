#!/usr/bin/python3

__all__ = [
    'EDGE_WEIGHT_KEY', 'NODE_SWITCH_CAPACITY_WEIGHT_KEY', 'NODE_CPU_WEIGHT_KEY', 'SWITCH_CAPACITY_IMBALANCE_FACTOR',
    'VHOST_CPU_IMBALANCE_FACTOR', 'INIT_SWITCH_CPU_SHARES', 'SWITCH_CPU_SHARE_UPDATE_FACTOR',
    'PM_UNDER_UTILIZED_THRESHOLD', 'PM_UNDER_UTILIZED_PORTION_RESERVE_RATIO', 'PM_OVER_UTILIZED_THRESHOLD'
]

# The attribute for edge's weight. If changed, must update graph_model as well.
EDGE_WEIGHT_KEY = 'weight'

# The attribute for node's switch capacity requirement value.
NODE_SWITCH_CAPACITY_WEIGHT_KEY = 'weight'

# The attribute for node's CPU requirement value.
NODE_CPU_WEIGHT_KEY = 'cpu'

# To what extent do we allow for imbalance on switch capacity constraint?
# We allow for some delta so that
# (1) graph shape helps reduce search space and
# (2) resource limit fits graph shape better.
SWITCH_CAPACITY_IMBALANCE_FACTOR = 0.02

# To what extent do we allow for imbalance on CPU constraint? +/- 15%.
VHOST_CPU_IMBALANCE_FACTOR = 0.1

# Switch CPU shares that will be assigned to every PMs in the first round.
INIT_SWITCH_CPU_SHARES = 20

# Coefficient for updating switch CPU share of PMs. next = a*old + (1-a)*would_be.
SWITCH_CPU_SHARE_UPDATE_FACTOR = 0.4

# We consider the PM to be under-utilized if there is 10% (or, 0.1) of total CPU share unused.
PM_UNDER_UTILIZED_THRESHOLD = 0.1

# For the under-utilized portion, we reserve 70% and allocate 30% proportionally to switch and vhost shares.
PM_UNDER_UTILIZED_PORTION_RESERVE_RATIO = 0.7

# We consider the PM to be over-utilized if total CPU share needed on the PM is 10% more than its maximum.
PM_OVER_UTILIZED_THRESHOLD = 0.05

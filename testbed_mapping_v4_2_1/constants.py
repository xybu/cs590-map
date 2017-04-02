__all__ = (
    'EDGE_WEIGHT_KEY', 'NODE_SWITCH_CAPACITY_WEIGHT_KEY', 'NODE_CPU_WEIGHT_KEY', 'DEFAULT_SW_IMBALANCE_FACTOR',
    'DEFAULT_VHOST_IMBALANCE_FACTOR', 'INIT_SWITCH_CPU_SHARES', 'SWITCH_CPU_SHARE_UPDATE_FACTOR',
    'PM_UNDER_UTILIZED_THRESHOLD', 'PM_UNDER_UTILIZED_PORTION_ALLOC_RATIO', 'PM_OVER_UTILIZED_THRESHOLD',
    'INIT_DOMINANCE_TOLERANCE'
)

# The attribute for edge's weight. If changed, must update graph_model as well.
EDGE_WEIGHT_KEY = 'weight'

# The attribute for node's switch capacity requirement value.
NODE_SWITCH_CAPACITY_WEIGHT_KEY = 'weight'

# The attribute for node's CPU requirement value.
NODE_CPU_WEIGHT_KEY = 'cpu'

INIT_DOMINANCE_TOLERANCE = 48

# To what extent do we allow for imbalance on switch capacity constraint?
# We allow for some delta so that
# (1) graph shape helps reduce search space and
# (2) resource limit fits graph shape better.
DEFAULT_SW_IMBALANCE_FACTOR = 0.08

# To what extent do we allow for imbalance on CPU constraint? +/- 15%.
DEFAULT_VHOST_IMBALANCE_FACTOR = 0.02

# Switch CPU shares that will be assigned to every PMs in the first round.
INIT_SWITCH_CPU_FIXED = False
INIT_SWITCH_CPU_SHARES = 20
INIT_SWITCH_CPU_FRAC = 0.9

# Coefficient for updating switch CPU share of PMs. next = a*old + (1-a)*would_be.
SWITCH_CPU_SHARE_UPDATE_FACTOR = 0.4

# Branch when the fraction overloaded PMs / total PMs is no less than this threshold.
BRANCH_THRESHOLD = 0.5

# We consider the PM to be under-utilized if less than 90% of CPU shares of a PM is used.
PM_UNDER_UTILIZED_THRESHOLD = 0.9

# We consider the PM to be over-utilized if total CPU share allocated to the PM is more than 110% of its maximum.
PM_OVER_UTILIZED_THRESHOLD = 1.05

# For the under-utilized portion, we allocate 30% to next round.
PM_UNDER_UTILIZED_PORTION_ALLOC_RATIO = 0.3

SHARE_ADJUSTMENT_NEW_ALPHA = 1

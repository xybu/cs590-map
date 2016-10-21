Some thoughts:

Without moving average, when the most capable PM is over-utilized its CPU share for packet processing becomes 0. Then its capacity value becomes 0 and is essentially disabled. Then all nodes are moved out of this PM and it becomes most capable again. We basically end up with a "wilder" loop.

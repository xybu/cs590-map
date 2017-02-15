The objective of v5 is to revisit the share adjustment phase:

# Current share adjustment phase

So the flow works as follows:

1. Convert absolute-valued input (CPU shares) into normalized values (fractions).
2. Execute METIS and obtain assignment.
3. From assignment calculate usages.
4. Use usages as base for next input, and adjust the values according to the PM utilization status.

The problem is that, this next input, after converted to normalized values, may not preserve the
trend (for each PM, up or down, by how much) and relationship (e.g., PM A should take more load than PM 
B) we desire (e.g., we want to increase fraction for A, but after adjustment fraction for A may 
decrease).

# Ideas

1. Only use fractions as input. Absolute-valued input is converted and printed only for readability.

2. We want to adjust shares to improve fidelity (i.e., reduce values by Tier 1 criteria -- degree of over-utilization,
   and min cut), to use less resource.

~~Some thoughts:~~

~~Without moving average, when the most capable PM is over-utilized its CPU share for packet processing becomes 0. Then its capacity value becomes 0 and is essentially disabled. Then all nodes are moved out of this PM and it becomes most capable again. We basically end up with a "wilder" loop.~~

# Thoughts

 - The assignment will need at least ceiling((sum of CPU weights) / 100) hosts no matter how capable the most powerful PM is.

 - It's not a good idea to start the algorithm with "all PMs use 90% of CPU processing packets" because most
 CPU will be used by the nodes (still depending on capacity function though).
 
 - The goal calculation code uses residual node weight sum as weight for each set. Is it better to allocate the node weight sum proportionally?

# Changes

 (1) Disabled moving average -- the next usage value is simply the remaining CPU share left from the nodes assigned. Later change: add coefficient for damping (like how TCP RTT is calculated).
 
 (2) Stop at duplication -- if any assignment appears twice stop and return this assignment.
 
 (3) Instead of giving 90% CPU share to packet processing at the beginning, use (100% - (sum_of_CPU_weights) / (active_hosts)). Later change: use the most pessimistic value.

# Findings

 (1) MKL can still assign nodes to a set whose target weight is 0. See original case study 80.

 (2) For a capacity function that is "sharp", a slight increase in CPU share for packet processing can lead to huge jump in capacity, which in turn leads to more nodes being allocated there, which then drastically reduces capacity.

 (4) Without moving avg (damping), if there are two powerful PMs and mapping results in one (A) being under-utilized and the other (B) being over-utilized, capacity of B will be sharply cut and become A in the next round; A will become B in the next round.

 (5) Should we allow for two hosts to be under-utilized? Like, one host uses 89% and the other 88%. It's not that different from (90%, 87%).

 (3) The capacity function "0 17600 -235200" is not valid because part of its codomain is negative on the domain. A valid function should be f(x): [0, 100] -> R+.

# Questions

 (1) If max processing power can't accommodate all the nodes, then all PMs can be stressed. Stop condition for this?

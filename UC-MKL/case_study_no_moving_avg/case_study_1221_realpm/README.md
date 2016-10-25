Compared to the original test case 1221, capacity functions are replaced with
the ones found (in Section IV) on the paper draft.

```
# PM 0 -- 2Core @ 1.20GHz
0 3920668 -3838597
# PM 1 -- 2Core @ 2.39GHz
0 7339637 -55472306
# PM 2 -- 4Core @ 1.20GHz
57498 4490990 40612926
# PM 3 -- 4Core @ 1.20GHz
44591 12671848 9483925
```

## Behavior

We see that the program ran three iterations. Because PM #0 and PM #1 were
insignificant, they were ignored in the description below.

In the first iteration, it believed PM #3 could host the whole topology with 20%
CPU share allocated to packet processing. But it turned out not working because
the sum of CPU shares needed by vhosts far exceeded 100%. Its packet processing
CPU share was changed to 14% for the next round. The other three PMs were
upgraded.

```
PM 2 is under-utilized. Its CPU usage is 0 + 20 = 20.
  |- Accum. usage=20.00, New usage=100.00, Next usage=68.

PM 3 is over-utilized. Its CPU usage is 410 + 20 = 430.
  |- Accum. usage=20.00, New usage=10.00, Next usage=14.
```

In the second iteration, same mistake as first iteration was made but on PM #2.
After this iteration, PM #2 was downgraded and PM #3 was upgraded.

```
PM 2 is over-utilized. Its CPU usage is 410 + 68 = 478.
  |- Accum. usage=68.00, New usage=10.00, Next usage=33.

PM 3 is under-utilized. Its CPU usage is 0 + 14 = 14.
  |- Accum. usage=14.00, New usage=100.00, Next usage=65.
```

The third round was same as the first round, so the program stopped.

If there were one more round, the following CPU share for packet processing
will be used:

```
PM 2 is under-utilized. Its CPU usage is 0 + 33 = 33.
  |- Accum. usage=33.00, New usage=100.00, Next usage=73.

PM 3 is over-utilized. Its CPU usage is 410 + 65 = 475.
  |- Accum. usage=65.00, New usage=10.00, Next usage=32.
```

## Problem

In this test PM #2 and #3 each has the power to process the packets that will
flow in the network, but neither has the power to fulfill CPU requirement
of vhosts.

The program failed to give a correct answer because after choosing one in PM #2
and #3, the other PM is largely freed, which will result in an even larger
capacity in the next round -- say, round R -- which will be even worse than
round R-2.

## Thoughts

Maybe we don't adjust a PM's CPU share for packet processing unless this PM
is involved in the current round?

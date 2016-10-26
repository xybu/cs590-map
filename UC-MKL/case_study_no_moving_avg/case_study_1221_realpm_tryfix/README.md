A follow-up to [case_study_1221_realpm](../case_study_1221_realpm). It changed the algorithm so that only the PMs involved 
in current iteration will be updated.

With this change, the program is able to allocate the topology to two PMs, but the result is still wrong. The program
should pick up at least three PMs.

```
PM 0 is disabled in this iteration.

PM 1 is disabled in this iteration.

PM 2 is over-utilized. Its CPU usage is 143 + 10 = 153.
  |- Accum. usage=10.00, New usage=10.00, Next usage=10.

PM 3 is over-utilized. Its CPU usage is 267 + 10 = 277.
  |- Accum. usage=10.00, New usage=10.00, Next usage=10.
  
Iteration 1 gives same assignment as 0. Stop.
```

The program thinks that PM #2 and #3 can well address the topology because the sum of their capacity at 10% CPU share for packet processing exceeds sum of vhost weights but they can't. And it's a situation where the program cannot make progress.

TODO: Start from the worst case and work towards better solution?

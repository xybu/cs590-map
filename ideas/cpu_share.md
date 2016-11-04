A scheme of `[0, 100%]` is not good enough to distinguish the different numbers of cores on PMs. The percents are not
comparable.

A better scheme would be `[0, NCores * 100%]`. This takes the number of cores into consideration, but use such a value across PMs indicates that we ignore the difference in single-core computational power (e.g., assume 5% on a Pentium II 450MHz core gives same power as 5% on a Skylake 4GHz core).

This directory contains the output of UC-MKL program with the "k'-1" change.

Compared to the original case_study_80, a way more capable PM (PM #5) is added in the input.

We see that

 1. The program initially thought that PM #5 can host everything because its capacity is way larger than the sum of node weights.
 2. It then tried and found that CPU usage would be too high (line 221 of 80.stdout).
 3. It then sharply reduced the capacity of PM #5 and picked two more hosts (PM #1 and PM #4, both have same cap function).
 4. It then found that PM #1, #4, and #5 all would use too much CPU (line 360 of 80.stdout).
 5. It reduced the power for packet processing on PMs #1 and #4 then repeated. PM #4 was good now; PM #1 used slightly less CPU; PM #5 
    slightly more (line 499 of 80.stdout).
 6. It adjusted the balance between PM #1 and PM #4 and tried again. Now both were fine and PM #5 still too high.
 7. Infinite loop with no changes. The algorithm believed stubbornly that the mapping can be accommodated by PM #1, 4, and 5 but kept finding
    that PM #5 had too much CPU used.

A different run introduced (a trivial portion of) the next most capable PM but didn't help.

It seems the capping on PM CPU usage when calculating moving average prevented further, different trials.

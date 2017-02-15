How do we rank the partition result?

The major factors are:

 * Number of PMs used.
 * Number of overloaded PMs.
 * Number of under-utilized PMs.
 * Min cut.

And we can use the extent to which a PM is over-utilized or under-utilized to further distinguish
the results.

Say, we have 4 PMs each of which is in one of the four states: not-used, under, ok, over.

| Unused   | Under | OK | Over | Comment                 |
| -------- | ----- | -- | ---- | ----------------------- |
| 4        | 0     | 0  | 0    | Invalid.                |
| 3        | 1     | 0  | 0    | Too much resource.      |
| 3        | 0     | 1  | 0    | One PM is sufficient.   |
| 3        | 0     | 0  | 1    | Questionable.           |
| 2        | 2     | 0  | 0    | ??                      |
| 2        | 0     | 2  | 0    |                         |
| 2        | 0     | 0  | 2    |                         |
| 2        | 1     | 1  | 0    |                         |
| 2        | 1     | 0  | 1    |                         |  
| 2        | 0     | 1  | 1    |                         |
| 1        | 3     | 0  | 0    |                         |
| 1        | 0     | 3  | 0    |                         |
| 1        | 0     | 0  | 3    |                         |
| 1        | 1     | 2  | 0    |                         |
| 1        | 1     | 0  | 2    |                         |
| 1        | 0     | 1  | 2    |                         |
| 1        | 0     | 2  | 1    |                         |
| 1        | 2     | 0  | 1    |                         |
| 1        | 2     | 1  | 0    |                         |
| 0        | 4     | 0  | 0    |                         |
| 0        | 0     | 4  | 0    |                         |
| 0        | 0     | 0  | 4    | Insufficient resource.  |
| 0        | 1     | 3  | 0    |                         |
| 0        | 1     | 0  | 3    |                         |
| 0        | 0     | 1  | 3    |                         |
| 0        | 0     | 3  | 1    |                         |
| 0        | 2     | 2  | 0    |                         |
| 0        | 2     | 0  | 2    |                         |
| 0        | 0     | 2  | 2    |                         |
| 0        | 3     | 1  | 0    |                         |
| 0        | 3     | 0  | 1    |                         |

We divide the result to two tiers -- no over PMs (T0) and other (T1).

For tier 1

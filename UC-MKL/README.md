UC-MKL
======

Code repository. Case studies.

## Input Format

```
Chaco graph file name
Host CPU requirement file name
Assignment output file name
Global partitioning method -- 1=MKL, 2=Spectral, 5=Linear, ...
Number of vertices coarsen down to
Total number of target hypercube dimensions
PM 1 -- 0 17600 -235200
PM 2 -- 200 53800 -210100  
PM 3 -- 0 37600 6000
PM 4 -- 0 17600 -235200
PM 5 -- 0 17600 -235200
PM 6 -- 200 53800 -210100 
PM 7 -- 0 17600 -235200
PM 8 -- 200 53800 -210100
Partitioning dimension -- 1=Bi, 2=Quad, 3=Oct
Run another program? -- yYnNqQxX (i.e., 'n')
```

## Known Issues

1. Number of PMs is hardcoded to be 8.

2. Program writes to output file only if it ends early.


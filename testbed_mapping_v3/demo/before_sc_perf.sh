#!/bin/bash

for case_name in $(ls before_sc_perf) ; do
    path="./before_sc_perf/$case_name"
    echo $path
    rm -f $path/*.pdf $path/*.svg $path/*.csv $path/output.txt $path/best_assignment*.txt
    ../main.py -g $path/graph.txt \
               -p $path/pms.txt \
               -c $path/host.txt \
               -o $path --find-iv &> $path/output.txt
done

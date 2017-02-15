#!/bin/bash

for path in $(find ./before_sc_perf/* -maxdepth 0 -type d -print) ; do
    echo $path
    rm -f $path/*.pdf $path/*.svg $path/*.csv $path/output.txt $path/best_assignment*.txt
    ../main.py -g $path/graph.txt \
               -p $path/pms.txt \
               -c $path/host.txt \
               -o $path --find-iv # &> $path/output.txt
done

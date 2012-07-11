#!/bin/sh

for f in $CQA_HOME/analytic-module/R/*/; do
    if [ -f "$f/DESCRIPTION" ]
    then
        R CMD check --no-manual $f
    fi
done

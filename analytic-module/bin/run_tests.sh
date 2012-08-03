#!/bin/sh

if [ ! -z $1 ]
then
    LIB="--library=$1"
fi


if [ ! -z $2 ]
then
    OUT="--outdir=$2"
else
    OUT="--outdir=$CQA_HOME/analytic-module/R/"
fi

for f in $CQA_HOME/analytic-module/R/*/; do
    if [ -f "$f/DESCRIPTION" ]
    then
        R CMD check --no-manual $LIB $OUT $f
    fi
done

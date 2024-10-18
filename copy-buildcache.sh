#! /bin/bash

find results-old -type d -name 'buildcache' -exec rsync -aR --relative {} ./results \;

mv results/results-old tmp
rm -rf results
mv tmp results

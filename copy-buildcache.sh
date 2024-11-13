#! /bin/bash

# Copy buildcache directories from results-old to results while preserving structure
# The sed command removes the 'results-old/' prefix from the destination path
find results-old -type d -name 'buildcache' -printf "%P\n" | while read -r path; do
    dest="results/$path"
    mkdir -p "$(dirname "$dest")"
    cp -r "results-old/$path" "$dest"
done

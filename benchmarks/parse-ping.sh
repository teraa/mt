#!/usr/bin/env bash

set -e

cd ping/

echo mode,min,avg,max,mdev
for file in *; do
    echo $(cut -d. -f1 <<< $file),$(tail -1 $file | cut -d' ' -f4 | tr '/' ',')
done
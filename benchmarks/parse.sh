#!/usr/bin/env bash

set -e

cd results

echo 'mode,send,recv'

for file in *.json; do
    mode=$(cut -d. -f1 <<< $file)
    jq ".end | [.sum_sent, .sum_received] | [\"$mode\", (.[].bits_per_second / 1000 | round)] | @csv" -r $file
done

#!/usr/bin/env bash

set -e

echo 'name,send,recv'
for file in *.json; do
    name=$(cut -d. -f1 <<< $file)
    jq ".end | [.sum_sent, .sum_received] | [\"$name\", .[].bits_per_second] | @csv" -r $file
done

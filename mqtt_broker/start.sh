#!/bin/bash

# coproc myfd { mosquitto -v; }

# exec 3>&${myfd[0]}
# echo "Hallo"
# python3 sub.py
# # mosquitto -v &
# # python3 sub.py

# IFS= read -d '' -u 3 output
# echo "$output"

echo "RUNNING A THING"
ls /data/images

python3 .
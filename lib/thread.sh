#!/bin/bash
for((i = 1; i <20; i++)) do
    screen -d -m python3 run_rpc.py
done

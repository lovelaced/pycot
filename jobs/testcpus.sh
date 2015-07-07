#!/bin/bash

dd if=/dev/urandom of=random.txt bs=1M count=$1

tar -czf rand1.gz random.txt &
tar -czf rand2.gz random.txt &
tar -czf rand3.gz random.txt &
tar -czf rand4.gz random.txt &

sleep 0.1
ps -F

wait $(jobs -p)

rm rand*.gz

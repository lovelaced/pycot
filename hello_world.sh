#!/bin/bash
# file name: sleep.sh

TIMETOWAIT="6"
echo "Hello world, I finally got out here"
ps -F
echo "sleeping for $TIMETOWAIT seconds"
/bin/sleep $TIMETOWAIT

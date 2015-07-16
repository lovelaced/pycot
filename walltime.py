import sys
import os

args = sys.argv[1:]
if len(args) is 1:
    filename = args[0]
else:
    print "Usage: walltime.py filename"
    exit(1)
directory = sys.path[0]

walltimes = {}
with open(directory + "/" + filename, 'r') as datafile:
    for line in datafile.readlines():
        line = line.split(" ")
        if walltimes.get(line[1]):
            if walltimes[line[1]] >= float(line[2]):
                continue
        walltimes[line[1]] = (float((line[2]))/60.0)/60.0

for key in walltimes:
    print key + ": " + str(walltimes.get(key)) + "hours"

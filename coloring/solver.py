#!/usr/bin/python
# -*- coding: utf-8 -*-
from Numberjack import *
import sys

sys.setrecursionlimit(10000)

def solveIt(inputData):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = inputData.split('\n')

    firstLine = lines[0].split()
    nodeCount = int(firstLine[0])
    edgeCount = int(firstLine[1])

    edges = []
    for i in range(1, edgeCount + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    colors = VarArray(nodeCount, 0, nodeCount)

    model = Model(
        # Minimise(sum(colors)), # this objective can sometimes yield a better solution
        Minimise(Max(colors)), # the math definition
        [AllDiff([colors[e[0]], colors[e[1]]]) for e in edges]
        [colors[i] <= Max(colors[0:i]) + 1 for i in range(2, nodeCount)] # symmetry breaking
    )

    lib = __import__('Mistral')
    solver = lib.Solver(model)
    # solver.setNodeLimit(5000000)
    # solver.setHeuristic("Impact")
    solver.setVerbosity(0)
    solver.setTimeLimit(60*60*4)
    solver.solve()

    # prepare the solution in the specified output format
    outputData = str(len(set(map(str, colors)))) + ' ' + str(0) + '\n'
    outputData += ' '.join(map(str, colors))

    return outputData


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fileLocation = sys.argv[1].strip()
        inputDataFile = open(fileLocation, 'r')
        inputData = ''.join(inputDataFile.readlines())
        inputDataFile.close()
        print solveIt(inputData)
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)'


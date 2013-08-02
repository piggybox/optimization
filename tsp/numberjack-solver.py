#!/usr/bin/python
# -*- coding: utf-8 -*-
from Numberjack import *
import math
import numpy as np
import sys
import networkx as nx
import itertools

sys.setrecursionlimit(10000)


def length(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def distance_matrix(points):
    matrix = np.zeros((len(points), len(points)))
    for idx1, p1 in enumerate(points):
        for idx2, p2 in enumerate(points):
            matrix[idx1, idx2] = length(p1, p2)

    return matrix

def less_only_combination(s, rest):
    result = []
    for i in s: 
        for j in rest:
            if i < j:
                result.append((i,j))
            if i > j:
                result.append((j,i))

    return result


def solveIt(inputData):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = inputData.split('\n')

    nodeCount = int(lines[0])
    node_list = range(nodeCount)

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append((float(parts[0]), float(parts[1])))


    dm = distance_matrix(points)

    path = Matrix(nodeCount, nodeCount) # 0,1 matrix to represent if a path is chosen 

    # objective funtion
    tmp = []
    for i in node_list:
        for j in range(i + 1, nodeCount): # only upper right corner of matrix is used
            tmp.append(dm[i, j] * path[i, j])
    
    obj = Sum(tmp)
    
    constrains = []
    # constraint 1: each node must be visited
    for i in node_list:
        exp = []
        for j in node_list:
            if i < j:
                exp.append(path[i, j])
            if i > j:
                exp.append(path[j, i])
        constrains.append(Sum(exp) == 2)

    # constraint 2: subtour elimination 
    for i in range(2, nodeCount - 1):
        for s in itertools.combinations(node_list, i):
            rest = set(node_list) - set(s)
            subtour_outer_relation = less_only_combination(s, rest)
            
            exp = []
            for (i,j) in subtour_outer_relation:
                exp.append(path[i,j])
            constrains.append(Sum(exp) >= 2)


    model = Model(
        Minimise(obj),
        constrains
        )

    print model

    lib = __import__('SCIP')
    solver = lib.Solver(model)
    # # solver.setNodeLimit(5000000)
    solver.setVerbosity(0)
    # # solver.setHeuristic('Impact')
    # # solver.setHeuristic('MinDomain', 'RandomMinMax', 2)
    # # solver.setHeuristic('DomainOverWDegree', 'RandomSplit', 2)
    solver.setTimeLimit(60)
    solver.solve()

    # calculate the length of the tour
    # obj = dm[solution[-1], solution[0]]
    # for index in range(0, nodeCount-1):
    #     obj += dm[solution[index], solution[index+1]]

    # prepare the solution in the specified output format
    outputData = str(obj.get_value()) + ' ' + str(0) + '\n'

    # rebuild graph from path matrix and 
    # traverse the path matrix to get the solution path
   
    g = nx.Graph()
    g.add_nodes_from(range(nodeCount))

    for i in node_list:
        for j in range(i + 1, nodeCount):
            if path[i,j].get_value() == 1:
                g.add_edge(i, j)

    last = 0            
    for x in range(1, nodeCount):
        if path[0, x].get_value() == 1:
            g.remove_edge(0, x)
            last = x
            break

    p = nx.dijkstra_path(g, 0, last)

    outputData += ' '.join(map(str, p))

    return outputData


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        fileLocation = sys.argv[1].strip()
        inputDataFile = open(fileLocation, 'r')
        inputData = ''.join(inputDataFile.readlines())
        inputDataFile.close()
        print solveIt(inputData)
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)'


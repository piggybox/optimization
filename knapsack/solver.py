from pulp import *
import uuid

def solveIt(inputData):

    # parse the input
    lines = inputData.split('\n')

    firstLine = lines[0].split()
    items = int(firstLine[0])
    capacity = int(firstLine[1])

    values = []
    weights = []

    for i in range(1, items+1):
        line = lines[i]
        parts = line.split()

        values.append(int(parts[0]))
        weights.append(int(parts[1]))

    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    sacks = LpVariable.dicts("item", range(items), lowBound=0, upBound=1, cat=LpInteger)
    total_value = [sacks[i] * v for i, v in zip(range(items), values)]
    total_weight = [sacks[i] * w for i, w in zip(range(items), weights)]

    prob = LpProblem("knapsack", LpMaximize)
    prob += (lpSum(total_value)), "total value"

    prob += (lpSum(total_weight) <= capacity)

    prob.writeLP("knapsack.lp")
    prob.solve(COIN(maxSeconds=60*120)) 

    
    # prepare the solution in the specified output format
    outputData = str(int(value(prob.objective))) + ' ' + str(0) + '\n'
    outputData += ' '.join([str(int(sacks[i].varValue)) for i in range(items)])
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
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)'


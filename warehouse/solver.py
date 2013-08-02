#!/usr/bin/python
# -*- coding: utf-8 -*-
# from Numberjack import *
from pulp import *
import uuid

def solveIt(inputData):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = inputData.split('\n')

    parts = lines[0].split()
    warehouseCount = int(parts[0])
    customerCount = int(parts[1])
    warehouse_list, customer_list = range(warehouseCount), range(customerCount)

    warehouse_cap, warehouse_cost = [], []
    for i in range(1, warehouseCount+1):
        line = lines[i]
        parts = line.split()
        warehouse_cap.append(int(parts[0])) 
        warehouse_cost.append(float(parts[1])) 

    customerSizes = []
    customerCosts = []

    # top 20 cheapest warehouse
    cheapest_warehouses = [x for x, y in sorted(enumerate(warehouse_cost), key=lambda x: x[1])[:20]]

    lineIndex = warehouseCount + 1
    for i in range(0, customerCount):
        customerSize = int(lines[lineIndex + 2 * i]) # demand size
        customerCost = map(float, lines[lineIndex + 2 * i + 1].split())
        customerSizes.append(customerSize)
        customerCosts.append(customerCost)


    # solution
    warehouse_list = cheapest_warehouses

    warehouse_open = LpVariable.dicts("warehouse", warehouse_list, lowBound=0, upBound=1, cat=LpInteger)
    customer_supplied = LpVariable.dicts("cw", [(c, w) for c in customer_list for w in warehouse_list], lowBound=0, upBound=1, cat=LpInteger)
    
    wc = lpSum([warehouse_open[i] * warehouse_cost[i] for i in warehouse_list])
    transportation_cost = lpSum([ customerCosts[c][w] * customer_supplied[c, w] for w in warehouse_list for c in customer_list])

    prob = LpProblem("warehouse", LpMinimize)
    prob += (wc + transportation_cost), "Total cost"


    for c in customer_list:
        # one customer -> one store
        prob += (lpSum([customer_supplied[c, w] for w in warehouse_list]) == 1) 

    for c in customer_list:
        for w in warehouse_list:
            # channel from customer to warehouse is open
            prob += (customer_supplied[c, w] <= warehouse_open[w]) 

    for w in warehouse_list:
        # each warehouse is within its capcacity
        prob += (lpSum([customer_supplied[c, w] * customerSizes[c] for c in customer_list]) <= warehouse_cap[w]) 


    prob.writeLP("warehouse" + str(uuid.uuid4()) + ".lp")
    prob.solve(COIN(maxSeconds=60*240)) 

    # prepare the solution in the specified output format
    outputData = str(value(prob.objective)) + ' ' + str(0) + '\n'

    for c in customer_list:
        for w in warehouse_list:
            if customer_supplied[c, w].varValue == 1:
               outputData += str(w) + ' '

    return outputData


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        fileLocation = sys.argv[1].strip()
        inputDataFile = open(fileLocation, 'r')
        inputData = ''.join(inputDataFile.readlines())
        inputDataFile.close()
        print 'Solving:', fileLocation
        print solveIt(inputData)
    else:
        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/wl_16_1)'


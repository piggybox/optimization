import math
from sklearn import cluster
from pulp import *


def distance(customer1, customer2):
    return math.sqrt((customer1[1] - customer2[1])**2 + (customer1[2] - customer2[2])**2)


def distance2center(customer, center):
    return math.sqrt((customer[1] - center[0]) ** 2 + (customer[2] - center[1]) ** 2)


def overload(customers, tour, capacity):
    return sum([customers[cid][0] for cid in tour]) - capacity


def distance_matrix(customers):
    matrix = {}
    # assume i < j
    for i in range(len(customers)):
        for j in range(i + 1, len(customers)):
                matrix[i, j] = length(customers[i], customers[j])

    return matrix 


def solveIt(inputData):
    # parse the input
    lines = inputData.split('\n')  

    customerCount, vehicleCount, vehicleCapacity = map(int, lines[0].split())
    depotIndex = 0 # warehouse

    customers = [] # 0 is the warehouse
    for i in range(1, customerCount + 1):
        line = lines[i]
        parts = line.split()
        # space, x, y
        customers.append((int(parts[0]), float(parts[1]),float(parts[2])))


    # use K-mean to get possible cluster centers for each vehicle
    kmcluster = cluster.KMeans(n_clusters=vehicleCount, init='random')
    kmcluster.fit([(x,y) for space, x, y in customers[1:]]) # exclude the warehouse at 0


    # group customers around cluster centers and balance vehicle capacity
    print kmcluster.cluster_centers_

    customer_list = range(1, customerCount)
    customer_allocation = LpVariable.dicts("ca", [(c, kc) for c in customer_list for kc in range(vehicleCount)], lowBound=0, upBound=1, cat=LpInteger)
    transporation_cost = lpSum([distance2center(customers[c], kmcluster.cluster_centers_[kc]) * customer_allocation[c, kc] for c in customer_list for kc in range(vehicleCount)])

    prob = LpProblem("customer allocation", LpMinimize)
    prob += transporation_cost

    # constraints
    for c in customer_list:
        # one customer can be picked by only one vehicle
        prob += (lpSum([customer_allocation[c, kc] for kc in range(vehicleCount)]) == 1)

    for kc in range(vehicleCount):
        # total customer orders is bound by vehicle capacity
        prob += (lpSum([customer_allocation[c, kc] * customers[c][0] for c in customer_list]) <= vehicleCapacity)

    prob.writeLP("customer_allocation.lp")
    prob.solve()
    print value(prob.objective)

    # assign to vehicle tour

    vehicleTours = [[] for i in range(vehicleCount)]
    for kc in range(vehicleCount):
        for c in customer_list:
            if customer_allocation[c, kc].varValue == 1:
                vehicleTours[kc].append(c)


    # calculate the cost of the solution; for each vehicle the length of the route
    obj = 0
    for v in range(vehicleCount):
        vehicleTour = vehicleTours[v]
        if len(vehicleTour) > 0:
            obj += distance(customers[depotIndex],customers[vehicleTour[0]])
            for i in range(0, len(vehicleTour) - 1):
                obj += distance(customers[vehicleTour[i]],customers[vehicleTour[i + 1]])
            obj += distance(customers[vehicleTour[-1]],customers[depotIndex])

    # prepare the solution in the specified output format
    outputData = str(obj) + ' ' + str(0) + '\n'
    for v in range(vehicleCount):
        outputData += str(depotIndex) + ' ' + ' '.join(map(str,vehicleTours[v])) + ' ' + str(depotIndex) + '\n'

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

        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/vrp_5_4_1)'


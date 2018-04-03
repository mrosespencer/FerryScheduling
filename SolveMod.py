from gurobipy import *
import time
import math


def ferrymodel(p, b, q, berths, porttimed, delta, portcostd, fuelcostd, capacity, demand, largetimed):
    t0 = time.time()

    # Create model
    m = Model()

    logname = "ferry-log"

    m.setParam("logfile", "%s.txt" % logname)

    n = p * q
    lam = 1
    demandlength = 42

    # Create Demand matrix

    dem = {}
    for a in range(demandlength):
        i = (demand[a, 0] - 1) * q + (demand[a, 2])
        ttime = largetimed[(demand[a, 0] - 1), (demand[a, 1] - 1)]
        for j in range(demand[a, 2] + ttime, demand[a, 3]):
            dem[i, j] = demand[a, 4]

    totaldemand = [0,0,0,0,0]
    for a in range(demandlength):
        for j in range(p):
            if demand[a,1] == (j+1):
                totaldemand[j]= totaldemand[j]+demand[a,4]
    # print(totaldemand)

    # Create variables
    x = {}
    y = {}

    for i in range(n):
        for j in range(n):
            for k in range(b):
                x[i, j, k] = m.addVar(vtype=GRB.INTEGER, name='x ' + str(i) + '_' + str(j))  # passengers
                y[i, j, k] = m.addVar(vtype=GRB.BINARY, name='y ' + str(i) + '_' + str(j) + '_' + str(b))  # ferries

    objective = LinExpr()
    for i in range(n):
        for j in range(n):
            for k in range(b):
                porti = math.floor(i / q)
                portj = math.floor(j / q)

                if porti != portj:
                    objective.addTerms(fuelcostd[k], y[i, j, k])
                else:
                    objective.addTerms(porttimed[k], y[i, j, k])

    for i in range(n):
        port = math.floor(i / q)
        m.addConstr((quicksum(y[i, j, k] for k in range(b) for j in range(n))) <= berths[port])  # berth constrain (3)
        for k in range(b):
            m.addConstr((quicksum(y[i, j, k] for j in range(n))) <= 1)  # ferry balancing(1)
            m.addConstr((quicksum(y[j, i, k] for j in range(n))) <= 1)

    for i in range(n):
        for j in range(n):
            for k in range(b):
                porti = math.floor(i / q)
                portj = math.floor(j / q)
                if porti != portj:
                    if (j / q) < ((q - 2) / q) * (portj + 1):
                        ptj = porttimed[portj]
                        m.addConstr(quicksum(y[l, m, k] for l in range(j + 1, (j + ptj))
                                             for m in range(j + 1, (j + ptj))) == ptj)  # load/unload (2)

    # home port balancing
    m.addConstr(y[q - 1, q - 1, 0] == 1)
    m.addConstr(y[3 * q - 1, 3 * q - 1, 1] == 1)
    m.addConstr(y[n - 1, n - 1, 2] == 1)

    for i in range(n):
        for j in range(n):
            for k in range(b):
                m.addConstr(x[i, j, k] <= capacity[k] * y[i, j, k])  # capacity constraint

    intotal = [0,0,0,0,0]
    outtotal = [0,0,0,0,0]

    intotal[0] = quicksum(x[i,j,k]*y[i,j,k] for i in range(q) for j in range(n) for k in range(b))
    outtotal[0] =quicksum(x[i,j,k]*y[i,j,k] for i in range(n) for j in range(q) for k in range(b))

    intotal[1] = quicksum(x[i, j, k]*y[i,j,k]  for i in range(q+1,2*q) for j in range(n) for k in range(b))
    outtotal[1] = quicksum(x[i, j, k]*y[i,j,k]  for i in range(n) for j in range(q+1,2*q) for k in range(b))

    intotal[2] = quicksum(x[i, j, k]*y[i,j,k]  for i in range(2*q + 1, 3 * q) for j in range(n) for k in range(b))
    outtotal[2] = quicksum(x[i, j, k]*y[i,j,k]  for i in range(n) for j in range(2*q + 1, 3 * q) for k in range(b))

    intotal[3] = quicksum(x[i, j, k]*y[i,j,k] for i in range(3*q + 1, 4 * q) for j in range(n) for k in range(b))
    outtotal[3] = quicksum(x[i, j, k]*y[i,j,k] for i in range(n) for j in range(3*q + 1, 4 * q) for k in range(b))

    intotal[4] = quicksum(x[i, j, k] for i in range(4*q + 1, 5 * q) for j in range(n) for k in range(b))
    outtotal[4] = quicksum(x[i, j, k] for i in range(n) for j in range(4*q + 1, 5 * q) for k in range(b))

    for l in range(p):
        m.addConstr((intotal[l] - outtotal[l] )== - totaldemand[l])


    m.update()
    return 1

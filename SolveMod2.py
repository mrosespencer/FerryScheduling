from gurobipy import *
import time
import math


def ferrymodel(p, b, q, berths, porttimed, delta, portcostd, fuelcostd, capacity, demand, times):
    t0 = time.time()

    # Create model
    m = Model()

    logname = "ferry-log"

    m.setParam("logfile", "%s.txt" % logname)

    n = p * q
    o = p*p

    # Create variables
    x = {}
    y = {}

    for i in range(q):
        for j in range(o):
            for k in range(b):
                # x[i, j, k] = m.addVar(vtype=GRB.INTEGER, name='x ' + str(i) + '_' + str(j))  # passengers
                y[i, j, k] = m.addVar(vtype=GRB.BINARY, name='y ' + str(i) + '_' + str(j) + '_' + str(b))  # ferries

    objective = LinExpr()
    for i in range(q):
        for j in range(o):
            for k in range(b):
                w = j%6

                if w != 0:
                    objective.addTerms(fuelcostd[k], y[i, j, k])
                else:
                    objective.addTerms(porttimed[k], y[i, j, k])

    # Ferry balancing constraints
    for k in range(b):
        for l in range(p):
            outb = quicksum(y[i,j,k] for i in range(q) for j in range(l*5, (l+1)*5))
            inb = quicksum(y[i,j,k] for i in range(q) for j in range(l, p*p, 5))
            m.addConstr(outb-inb == 0, name="bal" + str(l)+"_" + str(k))

    m.addConstr(y[(q-1), 0,0] == 1)
    m.addConstr(y[(q-1), 10,1] == 1)
    m.addConstr(y[(q - 1), 24, 2] == 1)

    # Berth constraints
    for i in range(q):
        for j in range(0,o, 6):
            port = j%5
            m.addConstr(quicksum(y[i,j,k] for k in range(b)) <= berths[port])

    # Traversing arc times
    for i in range(q):
        for j in range(o):
            for k in range(b):
                arctime = times[k,j]
                if (q-i) >= arctime:
                    if j%6 != 0:
                        m.addConstr(quicksum(y[a,j,k] for a in range(i,i+arctime)) ==1, name ="travel "+str(i)+"_"+str(k))  # this is definitely wrong
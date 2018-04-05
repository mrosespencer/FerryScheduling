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

    # Create variables
    x = {}
    y = {}

    for i in range(q):
        for j in range(p*p):
            for k in range(b):
                # x[i, j, k] = m.addVar(vtype=GRB.INTEGER, name='x ' + str(i) + '_' + str(j))  # passengers
                y[i, j, k] = m.addVar(vtype=GRB.BINARY, name='y ' + str(i) + '_' + str(j) + '_' + str(b))  # ferries

    objective = LinExpr()
    for i in range(q):
        for j in range(p*p):
            for k in range(b):
                w = j%6

                if w != 0:
                    objective.addTerms(fuelcostd[k], y[i, j, k])
                else:
                    objective.addTerms(porttimed[k], y[i, j, k])

    for k in range(b):
        for l in range(p):
            outb = quicksum(y[i,j,k] for i in range(q) for j in range(l*5, (l+1)*5))
            inb = quicksum(y[i,j,k] for i in range(q) for j in range(l, p*p, 5))
            m.addConstr(outb-inb == 0, name="bal" + str(l)+"_" + str(k))
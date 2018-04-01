from gurobipy import *
import time
import math


def ferrymodel(p, b, q, berths, porttimed, delta, portcostd, fuelcostd, capacity, demand, largetimed):
    t0 = time.time()

    # Create model
    m = Model()

    logname = "ferry-log"

    m.setParam("logfile", "%s.txt" % logname)

    n = b * q
    lam = 1
    demandlength = 42


    # Create Demand matrix

    dem = {}
    for a in range(demandlength):
        i = (demand[a,0]-1)*q+(demand[a,2])
        ttime = largetimed[(demand[a,0]-1), (demand[a,1]-1)]
        for j in range(demand[a,2]+ttime, demand[a,3]):
            dem[i,j] = demand[a,4]



    # Create variables
    x = {}
    y = {}

    for i in range(n):
        for j in range(n):

            x[i, j] = m.addVar(vtype=GRB.INTEGER, name='x ' + str(i) + '_' + str(j))

            for k in range(b):
                y[i, j, k] = m.addVar(vtype=GRB.BINARY, name='y ' + str(i) + '_' + str(j) + '_' + str(b))

    objective = LinExpr()
    for i in range(n):
        for j in range(n):
            for k in range(b):
                porti = math.floor(i / q)
                portj = math.floor(j / q)

                if porti != portj:
                    objective.addTerms(fuelcostd[k], y[i,j,k])
                else:
                    objective.addTerms(porttimed[k],y[i,j,k])


    for i in range(n):
        port = math.floor(i/q)
        m.addConstr((quicksum(y[i,j,k] for k in range(b) for j in range(n))) <=  berths[port])  # berth constrain (3)
        for k in range(b):
            m.addConstr((quicksum(y[i,j,k] for j in range(n))) <= 1)    # ferry balancing(1)

    for i in range(n):
        for j in range(n):
            for k in range(b):
                porti = math.floor(i / q)
                portj = math.floor(j / q)
                if porti != portj:
                    if (j/q) <((q-2)/q)*(portj+1):
                        ptj = porttimed[portj]
                        m.addConstr(quicksum(y[l,m,k] for l in range(j+1,(j+ptj))
                                             for m in range(j+1, (j+ ptj))) == ptj) # load/unload (2)

    # home port balancing
    m.addConstr(y[q-1,q-1,0] == 1)
    m.addConstr(y[3*q-1, 3*q-1, 1] == 1)
    m.addConstr(y[n-1,n-1,2] == 1)

    m.update()
    return 1
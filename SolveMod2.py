from gurobipy import *
import time
import math


def ferrymodel(p, b, q, berths, porttimed, delta, portcostd, fuelcostd, capacity, demand, times, largetimed):
    t0 = time.time()

    # Create model
    m = Model()

    logname = "ferry-log"

    m.setParam("logfile", "%s.txt" % logname)
    m.setParam(GRB.Param.TimeLimit, 90.0)

    n = p * q
    o = p*p
    # print(q)

    # Create variables
    x = {}
    y = {}

    for i in range(q):
        for j in range(o):
            for k in range(b):
                # x[i, j, k] = m.addVar(vtype=GRB.INTEGER, name='x ' + str(i) + '_' + str(j))  # passengers
                y[i, j, k] = m.addVar(vtype=GRB.BINARY, name='y ' + str(i) + '_' + str(j) + '_' + str(k))  # ferries

    for i in range(q+1):
        for j in range(o):
            for k in range(p):
                x[i, j, k] = m.addVar(vtype=GRB.INTEGER, name='x ' + str(i) + '_' + str(j)+ '_' + str(k))  # passengers

    objective = LinExpr()
    for i in range(q):
        for j in range(o):
            for k in range(b):
                w = j%6
                arctime = times[k, j]

                if w != 0:
                    objective.addTerms(fuelcostd[k]*arctime, y[i, j, k])
                else:
                    objective.addTerms(porttimed[k], y[i, j, k])

    # Ferry balancing constraints
    for k in range(b):
        for l in range(p):
            outb = quicksum(y[i,j,k] for i in range(q) for j in range(l*5, (l+1)*5))
            inb = quicksum(y[i,j,k] for i in range(q) for j in range(l, p*p, 5))
            m.addConstr(outb-inb == 0, name="bal " + str(l)+"_" + str(k))

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
                        m.addConstr(quicksum(y[a,j,k] for a in range(i,i+arctime)) <= 1, name ="travel "+str(i)+"_"+str(k))  # this is possibly wrong

    # Waiting arc times
    for i in range(q-3):
        for j in range(o):
            for k in range(b):
                port = j%5
                arctime = times[k, j]
                w = porttimed[port]
                if (q - i) > arctime + w:
                    m.addConstr(w*(quicksum(y[l,j,k] for l in range(i+1+arctime, i+w+arctime))) >= y[i,j,k], name = "wait " +str(i)+"_"+str(j)+"_"+str(k))    #not convinced this is right either

    for i in range(q):
        for j in range(o):
            if j % 6 != 0:
                m.addConstr(quicksum(x[i,j,a] for a in range(p)) <= quicksum(capacity[k]*y[i,j,k] for k in range(b)), name = "cap "+str(i)+"_"+str(j)) # capacity constraints

    # Passenger balancing -- needs modification
    for a in range(p):
        for l in range(p):
            for i in range(q):
                outx = quicksum(x[i,j,a]  for j in range(l*5, (l+1)*5))
                inx = quicksum(x[i,j,a]  for j in range(l, p*p, 5))
                # print("%d, %d, %d" % (i, l, a))
                m.addConstr(inx-outx == demand[i,l,a], name="bal " +str(i)+"_"+ str(l)+"_" + str(a))

    # Passenger transfer
    for a in range(p):  #destination port
        for i in range(9,q-1):
            w = porttimed[a]
            for t in range(i, i+w):

                # l = 2
                for l in range(p):  #transfer port
                    if l!= a:
                        arctime = [0,0,0,0,0]

                        travelarcs = []
                        for q in range(p):
                            if q != a:
                                if q != l:
                                    travelarcs.append(q)    #list of travel arcs possible for the transfer and destination ports
                        arctime[q] = largetimed[q, l]
                        sum = LinExpr()
                        for j in range(i, t):
                            for q in range(p):
                                if q != a:
                                    if q != l:
                                        sum.addTerms(1.0, x[(j-arctime[q]), (q*p +l), a])

                        m.addConstr(sum <= x[t, l*6,a], name= "transfer " +str(i)+"_"+ str(l)+"_" + str(a))


                        # print(sum)

                    # print(travelarcs)


                # lhs = quicksum(x[i,,a] for j =)



    m.update()
    m.optimize()


    finalx = {}
    varlist = []

    # for v in m.getVars():
    #     if v.VType  > 0:
    #         varlist.append(v.x)


    # for i in range(n):
    #     for j in range(n):
    #         finalx[i,j] = varlist[(n*i)+j]

    # gap = m.MIPGAP
    #
    # m.computeIIS()
    # m.write("model.ilp")
    # print('\nThe following constraint(s) cannot be satisfied:')
    # for c in m.getConstrs():
    #     if c.IISConstr:
    #         print('%s' % c.constrName)

    # for v in m.getVars():
    #     if v.x > 0:
    #         print(v.varName, v.x)

    # print('Obj:', m.objVal)
    # print('Gap: ', gap)


    t1 = time.time()
    totaltime = t1 - t0
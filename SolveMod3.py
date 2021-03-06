from gurobipy import *
import time
import math


def ferrymodel(p, b, q, berths, porttimed, delta, portcostd, fuelcostd, capacity, demand, times, largetimed, n, boatbalance):
    t0 = time.time()
    # print(q)

    # Create model
    m = Model()

    logname = "ferry-log"

    m.setParam("logfile", "%s.txt" % logname)
    m.setParam(GRB.Param.TimeLimit, 90.0)
    # m.setParam(GRB.Param.Presolve, 0)

    # n = p * q
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

    for i in range(q + 1):
        for j in range(o):
            for k in range(n):
                x[i, j, k] = m.addVar(vtype=GRB.INTEGER, name='x ' + str(i) + '_' + str(j) + '_' + str(k))  # passengers

    objective = LinExpr()
    for i in range(q):
        for j in range(o):
            for k in range(b):
                w = j % 6
                arctime = times[k, j]

                if w != 0:
                    objective.addTerms(fuelcostd[k] * arctime, y[i, j, k])
                else:
                    objective.addTerms(portcostd[k], y[i, j, k])

    bigm = 100000

    # for i in range(q):
    #     for j in range(o):
    #         for l in range(n):
    #             w = j%6
    #             if w != 0:
    #                 objective.addTerms(1.0, x[i, j, l])

    for j in range(o):
        for l in range(n):
            if j%6 !=0:
                objective.addTerms(bigm, x[q,j,l])



    m.setObjective(objective, GRB.MINIMIZE)

    # Ferry balancing constraints
    for k in range(b):
        for l in range(p):

            for i in range(q ):

                # arctime = [0, 0, 0, 0, 0]
                # for h in range(p):
                #     arctime[h] = largetimed[h, l]
                # arctime[l] = 1

                inb = LinExpr()
                for j in range(l, o, 5):
                    # port = j % 5
                    arctime = times[k, j]
                    if arctime == 0:
                        arctime = 1
                    if i-arctime >= 0:
                        inb.add(y[i - arctime, j, k])
                # print(inb)
                outb = quicksum(y[i, j, k] for j in range(l * 5, (l + 1) * 5))
                # inb = quicksum(y[i,j,k] for i in range(q) for j in range(l, p*p, 5))
                m.addConstr((inb - outb) == boatbalance[i,l,k], name="boatbal " +str(i)+ "_"+ str(l) + "_" + str(k))



    for i in range(q):
        for k in range(b):
            m.addConstr(quicksum(y[i,j,k] for j in range(o)) <= 1, name= "arc "+ str(i) + "_" + str(k))

    # Berth constraints
    for i in range(q):
        for j in range(0, o, 6):
            port = j % 5
            m.addConstr(quicksum(y[i, j, k] for k in range(b)) <= berths[port], name= "berth " + str(i) + "_"+str(port))

    # Redundant constraints
    
    # # Traversing arc times
    # for k in range(b):
    #     for i in range(q):
    #         for l in range(p):
    #
    #             arctime = times[k, j]
    #             if arctime ==0:
    #                 arctime =1
    #             if (q - i) >= arctime:
    #                 if arctime != 0:
    #                     m.addConstr(quicksum(y[a, l, k] for a in range(i, i + arctime) for l in range(o)) <= 1,
    #                                 name="travel " + str(i) + "_" + str(k))
    #
    # # Waiting arc times
    # for i in range(q - 3):
    #     for j in range(o):
    #         for k in range(b):
    #             port = j % 5
    #             arctime = times[k, j]
    #             w = porttimed[port]
    #             if (q - i) > arctime + w:
    #                 m.addConstr(
    #                     w * (quicksum(y[l, j, k] for l in range(i + 1 + arctime, i + w + arctime))) >= y[i, j, k],
    #                     name="wait " + str(i) + "_" + str(j) + "_" + str(k))

    for i in range(q ):
        for j in range(o):
            if j % 6 != 0:
                m.addConstr(
                    quicksum(x[i, j, a] for a in range(n)) <= quicksum(capacity[k] * y[i, j, k] for k in range(b)),
                    name="cap " + str(i) + "_" + str(j))  # capacity constraints

    # Passenger balancing -- needs modification
    for a in range(n):  # passenger group
        for l in range(p):  # all ports
            for i in range( q+1):
                # arctime = [0, 0, 0, 0, 0]
                # # travelarcs = []
                # for h in range(p):
                #     arctime[h] = largetimed[h, l]
                # arctime[l] = 1
                # inx = LinExpr()
                # for j in range(l, p * p, 5):
                #     port = int(math.floor(j / 5))
                #
                #     if i-arctime[port] >= 0:
                #
                #         inx.add(x[i - arctime[port], j, a])

                inx = LinExpr()
                for j in range(l, o, 5):
                    port = int(math.floor(j / 5))
                    arctime = largetimed[port, l]
                    if arctime == 0:
                        arctime = 1
                    if i-arctime >= 0:
                        # if arctime < q-i:
                        # print(arctime)
                        inx.add(x[i - arctime, j, a]) #fix for ferry times
                outx = quicksum(x[i, j, a] for j in range(l * 5, (l + 1) * 5))
                # inx = quicksum(x[i,j,a]  for j in range(l, p*p, 5))
                # print("%d, %d, %d" % (i, l, a))
                m.addConstr((inx - outx) == -demand[i, l, a], name="bal " + str(i) + "_" + str(l) + "_" + str(a)) #causes infeasibility



    # Passenger transfer
    for a in range(n):
        for i in range(q - 1):
            for l in range(p):   # transfer port
                w = porttimed[l]
                for k in range(p):  # destination port
                    for t in range(i, i + w-1):

                        sum = LinExpr()
                        for h in range(i, t):
                            for j in range(l,o,5):
                                port = int(math.floor(j / 5))
                                if k != port:

                                    arctime = largetimed[port, l]
                                    if arctime == 0:
                                        arctime = 1
                                    if i - arctime >= 0:
                                        sum.add(x[i - arctime, j, a])


                        m.addConstr(sum <= x[t, l * 6, a] , name="transfer " + str(i) + "_" + str(l) + "_" + str(a))

                        # arctime = [0, 0, 0, 0, 0]

                        # travelarcs = []
                        # for h in range(p):
                        #     if h != k:
                        #         if h != l:
                        #             travelarcs.append(
                        #                 h)  # list of travel arcs possible for the transfer and destination ports

                        # for j in range(i, t):
                        #         for h in range(p):
                        #             if h != k:
                        #                 if h != l:
                        #                     if j-arctime[h] >=0:
                        #                         sum.add(quicksum(x[(j - arctime[h]), (h * p + l), a] for a in range(n)))





    m.update()
    m.optimize()


    finalx = {}
    varlist = []


    # for i in range(n):
    #     for j in range(n):
    #         finalx[i,j] = varlist[(n*i)+j]

    gap = m.MIPGAP


    # m.computeIIS()
    # m.write("model.ilp")
    # print('\nThe following constraint(s) cannot be satisfied:')
    # for c in m.getConstrs():
    #     if c.IISConstr:
    #         print('%s' % c.constrName)

    for v in m.getVars():
        if v.x > 0:
            print(v.varName, v.x)

    print('Obj:', m.objVal)
    print('Gap: ', gap)




    t1 = time.time()
    totaltime = t1 - t0
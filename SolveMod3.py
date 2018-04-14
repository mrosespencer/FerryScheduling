from gurobipy import *
import time
import math


def ferrymodel(p, b, q, berths, porttimed, delta, portcostd, fuelcostd, capacity, demand, times, largetimed, n):
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

    bigm = 1000

    for i in range(q):
        for j in range(o):
            for l in range(n):
                w = j%6
                if w != 0:
                    objective.addTerms(1.0, x[i, j, l])

    for j in range(o):
        for l in range(n):
            port = j%5
            if l != port:
                objective.addTerms(bigm, x[q,j,l])



    m.setObjective(objective, GRB.MINIMIZE)

    # Ferry balancing constraints




    for k in range(b):
        for l in range(p):
            # for i in range(1,8):
            #     for h in range(l, o, 5):
                    # m.addConstr(y[i,h,k] -quicksum(y[i+1,a,k] for a in range(l * 5, (l + 1) * 5)) == 0, name="chillin " +str(i)+"_"+str(k))
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
                        # if arctime < q-i:
                        # print(arctime)
                        inb.add(y[i - arctime, j, k]) #fix for ferry times
                # print(inb)
                outb = quicksum(y[i, j, k] for j in range(l * 5, (l + 1) * 5))
                # inb = quicksum(y[i,j,k] for i in range(q) for j in range(l, p*p, 5))
                m.addConstr(inb - outb == 0, name="bal " + str(l) + "_" + str(k))

    m.addConstr(y[(0), 0, 0] == 1, name="home00")
    m.addConstr(y[(0), 10, 1] == 1, name="home10")
    m.addConstr(y[(0), 24, 2] == 1, name="home20")


    m.addConstr(y[(q -1), 0, 0] == 1, name="home0q")
    m.addConstr(y[(q -1), 10, 1]  == 1, name="home1q")
    m.addConstr(y[(q -1), 24, 2]  == 1, name="home2q")

    for i in range(q):
        for k in range(b):
            m.addConstr(quicksum(y[i,j,k] for j in range(o)) <= 1, name= "arc "+ str(i) + "_" + str(k))

    # Berth constraints
    for i in range(q):
        for j in range(0, o, 6):
            port = j % 5
            m.addConstr(quicksum(y[i, j, k] for k in range(b)) <= berths[port], name= "berth " + str(i) + "_"+str(port))

    # Traversing arc times
    for k in range(b):
        for i in range(q):
            for j in range(o):

                arctime = times[k, j]
                if arctime ==0:
                    arctime =1
                if (q - i) >= arctime:
                    if arctime != 0:
                        m.addConstr(quicksum(y[a, l, k] for a in range(i, i + arctime) for l in range(o)) <= 1,
                                    name="travel " + str(i) + "_" + str(k))  # this is possibly wrong

    # Waiting arc times
    # for i in range(q - 3):
    #     for j in range(o):
    #         for k in range(b):
    #             port = j % 5
    #             arctime = times[k, j]
    #             w = porttimed[port]
    #             if (q - i) > arctime + w:
    #                 m.addConstr(
    #                     w * (quicksum(y[l, j, k] for l in range(i + 1 + arctime, i + w + arctime))) >= y[i, j, k],
    #                     name="wait " + str(i) + "_" + str(j) + "_" + str(k))  # not convinced this is right either

    for i in range(q - 1):
        for j in range(o):
            if j % 6 != 0:
                m.addConstr(
                    quicksum(x[i, j, a] for a in range(n)) <= quicksum(capacity[k] * y[i, j, k] for k in range(b)),
                    name="cap " + str(i) + "_" + str(j))  # capacity constraints

    # Passenger balancing -- needs modification
    for a in range(n):  # destination
        for l in range(p):  # all ports
            for i in range(8, q+1):
                arctime = [0, 0, 0, 0, 0]
                # travelarcs = []
                for h in range(p):
                    arctime[h] = largetimed[h, l]
                arctime[l] = 1
                inx = LinExpr()
                for j in range(l, p * p, 5):
                    port = int(math.floor(j / 5))
                    if arctime[port] < 20:
                        inx.add(x[i - arctime[port], j, a])
                outx = quicksum(x[i, j, a] for j in range(l * 5, (l + 1) * 5))
                # inx = quicksum(x[i,j,a]  for j in range(l, p*p, 5))
                # print("%d, %d, %d" % (i, l, a))
                m.addConstr(inx - outx == -demand[i, l, a], name="bal " + str(i) + "_" + str(l) + "_" + str(a))

    # Passenger transfer
    for a in range(n):
        for i in range(9, q - 1):
            for k in range(p): # destination port
                w = porttimed[k]
                for t in range(i, i + w):

                # l = 2
                    for l in range(p):  # transfer port
                        if l != a:
                            arctime = [0, 0, 0, 0, 0]

                            travelarcs = []
                            for h in range(p):
                                if h != a:
                                    if h != l:
                                        travelarcs.append(
                                            h)  # list of travel arcs possible for the transfer and destination ports
                            arctime[h] = largetimed[h, l]
                            sum = LinExpr()
                            for j in range(i, t):
                                for h in range(p):
                                    if h != a:
                                        if h != l:
                                            if arctime[h] < 20:
                                                sum.addTerms(1.0, x[(j - arctime[h]), (h * p + l), a])

                            m.addConstr(sum <= x[t, l * 6, a], name="transfer " + str(i) + "_" + str(l) + "_" + str(a))


                        # print(sum)

                    # print(travelarcs)


                # lhs = quicksum(x[i,,a] for j =)



    m.update()
    m.optimize()


    finalx = {}
    varlist = []


    # for i in range(n):
    #     for j in range(n):
    #         finalx[i,j] = varlist[(n*i)+j]

    gap = m.MIPGAP


    m.computeIIS()
    m.write("model.ilp")
    print('\nThe following constraint(s) cannot be satisfied:')
    for c in m.getConstrs():
        if c.IISConstr:
            print('%s' % c.constrName)

    for v in m.getVars():
        if v.x > 0:
            print(v.varName, v.x)

    print('Obj:', m.objVal)
    print('Gap: ', gap)




    t1 = time.time()
    totaltime = t1 - t0
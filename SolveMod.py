from gurobipy import *
import time


def ferrymodel(p, b, q):
    t0 = time.time()

    # Create model
    m = Model()

    logname = "ferry-log"

    m.setParam("logfile", "%s.txt" % logname)

    n = b * q

    # Create variables
    x = {}
    y = {}

    for i in range(n):
        for j in range(n):

            x[i, j] = m.addVar(vtype=GRB.CONTINUOUS, name='x ' + str(i) + '_' + str(j))

            for k in range(b):
                y[i, j, k] = m.addVar(vtype=GRB.BINARY, name='y ' + str(i) + '_' + str(j) + '_' + str(b))

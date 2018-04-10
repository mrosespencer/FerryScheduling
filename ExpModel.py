import csv
import datetime
import SolveMod
import SolveMod2
import math

ports = 5
boats = 3
ferries = ["small1", "small2", "large"]
delta = 10


def printmatrix(m, r, c):
    line = []

    for i in range(r):
        for j in range(c):
            line.append(m[i, j])
        print(line)
        line = []


name = "times"

tname = "%s.txt" % name
ft = open(tname, "r")

# Time data
arrt = []
for line in ft:
    line = line.split()

    if line:
        line = [int(float(i)) for i in line]
        arrt.append(line)
ft.close()

small1time, small2time, largetime = ({} for b in ferries)

for i in range(ports):
    for j in range(ports):
        small1time[j, i] = arrt[j][i]
    for j in range(ports, ports * 2):
        small2time[j%5, i] = arrt[j][i]
    for j in range(ports * 2, ports * 3):
        largetime[j%5, i] = arrt[j][i]

largetimed ={}
for i in range(ports):
    for j in range(ports):
        largetimed[i,j] = math.floor(largetime[i,j]/delta)

# Time data
tname = "traveltime.txt"
ft = open(tname, "r")
arrtravel = []
for line in ft:
    line = line.split()

    if line:
        line = [int(float(i)) for i in line]
        arrtravel.append(line)
ft.close()

times = {}
for i in range(boats):
    for j in range(ports*ports):
        times[i,j] = math.floor(arrtravel[i][j]/delta)

# printmatrix(times,boats,ports*ports)

# Ferry data
homeport = [1, 3, 5]
capacity = [100, 100, 200]
fuelcost = [400, 400, 600]  # per hour
portcost = [160, 160, 240]  # per hour

# Port data
berths = [3, 2, 2, 1, 1]
porttime = [30, 20, 20, 20, 20]

# Demand data
arrd = []
with open('demand.csv', newline='') as fd:
    reader = csv.reader(fd)
    for row in reader:
        arrd.append(row)
fd.close()

demand = {}

# define parameters

starttime = '05:00'
pt = datetime.datetime.strptime(starttime, '%H:%M')
starttime = pt.minute + pt.hour * 60

finaltime = "23:50"
pt = datetime.datetime.strptime(finaltime, '%H:%M')
finaltime = pt.minute + pt.hour * 60

for i in range(len(arrd)):
    for j in range(5):
        demand[i, j] = arrd[i][j]
    demand[i, 0] = int(demand[i, 0])
    demand[i, 1] = int(demand[i, 1])
    demand[i, 4] = int(demand[i, 4])


for i in range(len(arrd)):
    for j in range(2, 4):
        pt = datetime.datetime.strptime(demand[i, j], '%H:%M')
        total_minutes = pt.minute + pt.hour * 60-starttime
        demand[i, j] = math.floor(total_minutes/delta)

# printmatrix(demand, len(arrd), 5)




q = int((finaltime-starttime)/delta)

fuelcostd = [0,0,0]
portcostd = [0,0,0]
for b in range(3):
    fuelcostd[b] = (fuelcost[b]*(delta/60))
    portcostd[b] = portcost[b] * (delta / 60)

porttimed = [0,0,0,0,0]
for p in range(ports):
    porttimed[p] = math.floor(porttime[p]/delta)

demandm ={}
# arrivingpass ={}
for i in range(q):
    # for j in range(p*p):
    #     demandm[i,j] =0
    for j in range(p):
        for h in range(p):
            demandm[i,j,h] =0

for i in range(len(arrd)):
    arrival = demand[i,0] - 1
    dest = demand[i,1] - 1
    arrtime = demand[i,2]
    desttime = demand[i,3]

    demandm[arrtime, arrival, dest] = demand[i,4]
    # demandm[desttime, (arrival*5 +dest)] = demand[i,4]
    # print(demandm[arrtime, arrival*5 +dest])

# printmatrix(demandm, q, 25)
# print(porttimed)

# SolveMod.ferrymodel(ports, boats, q, berths, porttimed,delta, portcostd, fuelcostd, capacity, demand, largetimed)
SolveMod2.ferrymodel(ports, boats, q, berths, porttimed,delta, portcostd, fuelcostd, capacity, demandm, times)
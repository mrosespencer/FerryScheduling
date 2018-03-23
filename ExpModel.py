import csv
import datetime
import SolveMod

ports = 5
boats = 3
ferries = ["small1", "small2", "large"]


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
        small2time[j, i] = arrt[j][i]
    for j in range(ports * 2, ports * 3):
        largetime[j, i] = arrt[j][i]

# Ferry data
homeport = [1, 3, 5]
capacity = [100, 100, 200]
fuelcost = [400, 400, 600]  # per hour
portcost = [160, 160, 240]

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

for i in range(len(arrd)):
    for j in range(5):
        demand[i, j] = arrd[i][j]
    demand[i, 0] = int(demand[i, 0])
    demand[i, 1] = int(demand[i, 1])
    demand[i, 4] = int(demand[i, 4])

for i in range(len(arrd)):
    for j in range(2, 4):
        pt = datetime.datetime.strptime(demand[i, j], '%H:%M')
        total_minutes = pt.minute + pt.hour * 60
        demand[i, j] = total_minutes

printmatrix(demand, len(arrd), 5)

# define parameters

delta = 10
initial = 0
final = 24 * 60

SolveMod.ferrymodel(p, b, final)

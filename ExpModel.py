# from gurobipy import *

ports = 5
boats = 3
ferries = ["small1", "small2", "large"]

name = "times"

tname = "%s.txt" % name
ft = open(tname, "r")

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
    for j in range(ports, ports*2):
        small2time[j, i] = arrt[j][i]
    for j in range(ports*2, ports*3):
        largetime[j, i] = arrt[j][i]


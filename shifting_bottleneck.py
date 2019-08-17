#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Shift import Shift
from jobShopIP import Job
        
filename = "/train/ta00"
#filename = '/zad5.txt'
flag = 2
import os
import sys
def main(argv):
    if len(argv) > 1:
        global filename 
        filename = argv[0]
        global flag
        flag = argv[1]
        flag = int(flag)*(-1)
    else:
        print("nazwisko ścieżka_do_folderu_z_danymi_wejściowymi -k")
        #sys.exit()
if __name__ == "__main__":
   main(sys.argv[1:])
filename = os.path.dirname(os.path.abspath(__file__)) + filename
with open(filename, "r") as file:
    NB_JOBS, NB_MACHINES = [int(v) for v in file.readline().split()]
    JOBS = [[int(v) for v in file.readline().split()] for i in range(NB_JOBS)]

MACHINES = [[JOBS[j][2 * s] for s in range(NB_MACHINES)] for j in range(NB_JOBS)]
DURATION = [[JOBS[j][2 * s + 1] for s in range(NB_MACHINES)] for j in range(NB_JOBS)]
js = Shift()
jobs = {}
for i in range(len(JOBS)):
    jobs[i] = Job(i,MACHINES[i], DURATION[i])
#jobs[1] = Job(1, [1,2,3], [10, 8, 4])
#jobs[2] = Job(2, [2,1,4,3], [8,3,5,6])
#jobs[3] = Job(3, [1,2,4], [4,7,3])
#jobs[1] = Job(1, [1,3,2], [7, 8, 10])
#jobs[2] = Job(2, [2,1,3], [6,4,12])
#jobs[3] = Job(3, [1,2,3], [8,8,7])

js.addJobs(jobs)
js.identical_paralel_m = flag
from timeit import default_timer as timer
t = timer()
while js.setted_up_machines != set(js.machines.keys()):
#    print(f'SETTED UP MACHINES: {js.setted_up_machines}')
    js.criticalPath
#    print(f'makespan = {js.makespan}')
    opt_m, list_of_opt_s, max_Lmax = js.computeLmax()
    #    js.output()
#    print(f'max_Lmax={max_Lmax},list_of_opt_s={list_of_opt_s}')
    if js.setted_up_machines == set(js.machines.keys()) and max_Lmax == 0 : break
    js.setted_up_machines.add(opt_m)
    new_edges = []
    
    for opt_s in list_of_opt_s:
        for i in range(len(opt_s)-1):
            new_edges.append((opt_s[i], opt_s[i+1]))
#    print(f'new_edges={new_edges}')
#    f = input('stop')
#    if f == 'n': sys.exit(0)
    js.add_edges_from(new_edges)
#    print('----------NEXT ITERATION----------')
total_time = timer() - t
output = js.output()
output += f'{js.makespan} {"{0:.3f}".format(total_time)}'
print(f'makespan: {js.makespan}')
print(f'Total execution time (sec): {"{0:.3f}".format(total_time)}\n')
print(output)
f = open(filename+'_sb_flag_'+str(flag)+'.out',"w+")
f.write(output)
f.close()
#def put_to_machine(identical_machines, i):
#    added = False
#    for mi, mtasks in identical_machines.items():
#        if len(mtasks)>0:
#            if mtasks[-1] == i:
#                identical_machines[mi].append(j)
#                added = True
#                break
#    if not added: 
#        min_l = float('inf')
#        add_to_mi = -1
#        for mi, mtasks in identical_machines.items():
#            if len(mtasks)<min_l:
#                min_l, add_to_mi = len(mtasks), mi
#        identical_machines[add_to_mi].append(i)
#        return add_to_mi
#for m in range(NB_MACHINES):
#    #print(f'm={m}')
#    identical_machines = {i:list() for i in range(js.identical_paralel_m)}
#    last_task = None
#    for i in sorted(js.machines[m]):
#        if i not in ("U", "V"):
#            for j in sorted(js.machines[m]):
#                if j not in ("U", "V"):
#                    if js.has_edge(i, j):
#                        add_to_mi = put_to_machine(identical_machines, i)
#                        #print(i,j)
#                        last_task = (add_to_mi, j)
#    identical_machines[last_task[0]].append(last_task[1])
#    ordered_tasks = set(task for tasks in identical_machines.values() for task in tasks)
#    not_ordered_tasks = set(js.machines[m]) - ordered_tasks
#    for task in not_ordered_tasks:
#        for mi in identical_machines.keys():
#            if identical_machines[mi] == list():
#                identical_machines[mi].append(task)
#                break
#    print(identical_machines)
#import matplotlib.pyplot as plt
#plt.rcParams["figure.figsize"] = [10,7]
#import networkx as nx
#pos = nx.shell_layout(js)
#nx.draw_networkx_nodes(js, pos, cmap=plt.get_cmap('jet'),  node_size = 10)
#nx.draw_networkx_labels(js, pos)
#nx.draw_networkx_edges(js, pos, edgelist=js.edges)
#plt.show()

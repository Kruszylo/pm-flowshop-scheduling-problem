
from docplex.cp.config import set_default, LOCAL_CONTEXT
from docplex.cp.model import CpoModel
import os
import sys
from timeit import default_timer as timer

set_default(LOCAL_CONTEXT)
pathes = sys.path
CPOPTIMIZER_PATH = '/Applications/CPLEX_Studio128/cpoptimizer/bin/x86-64_osx'
for p in pathes:
    if p.endswith('cpoptimizer/bin/x86-64_osx'):
        CPOPTIMIZER_PATH = p
os.environ['PATH'] += ':' + CPOPTIMIZER_PATH
mdl = CpoModel()
filename = "/train/ta01"
flag = 1
def main(argv):
    if len(argv) > 1:
        global filename 
        filename = argv[0]
        global flag
        flag = argv[1]
        flag = int(flag)*(-1)
    else:
        print("nazwisko ścieżka_do_folderu_z_danymi_wejściowymi -k")
        sys.exit(0)
if __name__ == "__main__":
   main(sys.argv[1:])
#-----------------------------------------------------------------------------
# Initialize the problem data
#-----------------------------------------------------------------------------

# Read the input data file.
# Available files are jobshop_ft06, jobshop_ft10 and jobshop_ft20
# First line contains the number of jobs, and the number of machines.
# The rest of the file consists of one line per job.
# Each line contains list of operations, each one given by 2 numbers: machine and duration
filename = os.path.dirname(os.path.abspath(__file__)) + filename
with open(filename, "r") as file:
    NB_JOBS, NB_MACHINES = [int(v) for v in file.readline().split()]
    JOBS = [[int(v) for v in file.readline().split()] for i in range(NB_JOBS)]

#-----------------------------------------------------------------------------
# Prepare the data for modeling
#-----------------------------------------------------------------------------

# Build list of machines. MACHINES[j][s] = id of the machine for the operation s of the job j
MACHINES = [[JOBS[j][2 * s] for s in range(NB_MACHINES)] for j in range(NB_JOBS)]

# Build list of durations. DURATION[j][s] = duration of the operation s of the job j
DURATION = [[JOBS[j][2 * s + 1] for s in range(NB_MACHINES)] for j in range(NB_JOBS)]

IDENTICAL_MACHINES_NUM = 4
Maschines = []
for i in range(NB_MACHINES):
    Maschines.append("M"+str(i))
    if i < IDENTICAL_MACHINES_NUM+1:
        for f in range(flag-1):
            Maschines.append("M"+str(i)+'e'+str(f+1))

Tasks = [[i for i in range(NB_MACHINES)] for j in range(NB_JOBS)]
#-----------------------------------------------------------------------------
# Build the model
#-----------------------------------------------------------------------------
#print(Maschines)
# Create model
mdl = CpoModel()
#if flag == 1:
#    # Create one interval variable per job operation
#    job_operations = [[mdl.interval_var(size=DURATION[j][m], name="J{}-{}".format(j, m)) for m in range(NB_MACHINES)] for j in range(NB_JOBS)]
#    
#    # Each operation must start after the end of the previous
#    for j in range(NB_JOBS):
#        for s in range(1, NB_MACHINES):
#            mdl.add(mdl.end_before_start(job_operations[j][s - 1], job_operations[j][s]))
#    
#    # Force no overlap for operations executed on a same machine
#    machine_operations = [[] for m in range(NB_MACHINES)]
#    for j in range(NB_JOBS):
#        for s in range(0, NB_MACHINES):
#            machine_operations[MACHINES[j][s]].append(job_operations[j][s])
#    for lops in machine_operations:
#        mdl.add(mdl.no_overlap(lops))
#    
#    # Minimize termination date
#    mdl.add(mdl.minimize(mdl.max([mdl.end_of(job_operations[i][NB_MACHINES - 1]) for i in range(NB_JOBS)])))
#
#else:
Durations = [[JOBS[j][2 * s + 1] for s in range(NB_MACHINES)] for j in range(NB_JOBS)]
Skills = [[("M"+str(JOBS[j][2 * s]),s) for s in range(NB_MACHINES)] for j in range(NB_JOBS)  ]
#append abilities of additional 5 machines
for j in range(NB_JOBS):
    for i in range(len(Skills[j])):
        if int(Skills[j][i][0][-1:]) < IDENTICAL_MACHINES_NUM+1:
            for f in range(flag-1):
                add_s = ('M' + str(int(Skills[j][i][0][-1:]))+'e'+str(f+1), Skills[j][i][1])
                Skills[j].append(add_s)
Precedences = [(i, i+1) for i in range(NB_MACHINES-1)]

tasks = {}
mtasks = {}
for j in range(NB_JOBS):
    for i,t in enumerate(Tasks[j]):
#        print((j,JOBS[j][2 * t],t),JOBS[j][2 * Tasks[j][-1] ])
        tasks[(j,JOBS[j][2 * t],t)] = mdl.interval_var(size = Durations[j][i], name="J{}-M{}".format(j, JOBS[j][2 * t]))
#    print("SKILLS")
    for s in Skills[j]:
#        print((j,s),"J{}-{}".format(j, s))
        mtasks[(j,s)] = mdl.interval_var(optional=True, name=str(j))#"J{}-{}".format(j, s)

for j in range(NB_JOBS):
#    print(j)
    for p in Precedences:
#        print((j,JOBS[j][2 * p[0]]),(j,JOBS[j][2 * p[1]]))
        mdl.add( mdl.end_before_start(tasks[j,JOBS[j][2 * p[0]],p[0]], tasks[j,JOBS[j][2 * p[1]],p[1]]) )
#for j in range(NB_JOBS):
#    for t in Tasks[j]:
#        print( (j,JOBS[j][2 * t]), [(j,s) for s in Skills[j] if s[0][:len('M'+str(JOBS[j][2 * t])) ] == 'M'+str(JOBS[j][2 * t]) and s[0][len('M'+str(JOBS[j][2 * t])): len('M'+str(JOBS[j][2 * t]))+1] in 'e'] )

for j in range(NB_JOBS):
    for t in Tasks[j]:
        mdl.add( 
                mdl.alternative(
                        tasks[j,JOBS[j][2 * t],t], 
                        [mtasks[j,s] for s in Skills[j] 
                        if s[0][:len('M'+str(JOBS[j][2 * t]))] == 'M'+str(JOBS[j][2 * t]) and s[0][len('M'+str(JOBS[j][2 * t])): len('M'+str(JOBS[j][2 * t]))+1] in 'e'
                        ] 
                        ) 
                )
for m in Maschines:
#    print([(j,s) for j in range(NB_JOBS) for s in Skills[j] if s[0]==m])
    mdl.add( mdl.no_overlap([mtasks[j,s] for j in range(NB_JOBS) for s in Skills[j] if s[0]==m]) )

# Minimize termination date
mdl.add(mdl.minimize(mdl.max([mdl.end_of(tasks[i,JOBS[i][2 * Tasks[i][-1] ],NB_MACHINES - 1]) for i in range(NB_JOBS)])))

#-----------------------------------------------------------------------------
# Solve the model and display the result
#-----------------------------------------------------------------------------
# Solve model
#print("Solving model....")
t = timer()
msol = mdl.solve(TimeLimit = 10 * 60, LogVerbosity = 'Quiet', Workers = 1) #in sec
total_time = timer() - t
#msol.print_solution()
#print(f'Total execution time: {total_time}')
#print("Solution: ")
#print("Cost will be "+str( msol.get_objective_values()[0] ))
output = ''
m_prime = Maschines[0]
machine_all_sol = []
for m in Maschines:
    if not m.startswith(m_prime):
        #new machine spotted
        m_prime = m
        machine_all_sol.sort(key=lambda tup:tup[1])
        for i in range(len(machine_all_sol)):
            output+=f'{machine_all_sol[i][0]} {machine_all_sol[i][1]} '
        output+='\n'
        machine_all_sol = []
    machine_sol = [msol.get_var_solution(mtasks[j,s]) for j in range(NB_JOBS) for s in Skills[j] if s[0]==m]
    list_of_tasks = []
    i=0
#    print(m)
    for sol in machine_sol:
        if sol!=None:
            start=sol.get_start()
#            print((i,start,sol.get_length(),sol.get_name()))
            if start!=None:
                
                list_of_tasks.append((sol.get_name(),start))
                i+=1
    machine_all_sol+=list_of_tasks
#output+=f'{m_prime}:'
machine_all_sol.sort(key=lambda tup:tup[1])
for i in range(len(machine_all_sol)):
    output+=f'{machine_all_sol[i][0]} {machine_all_sol[i][1]} '
output+='\n'
machine_all_sol = []
if msol.get_objective_values()!= None:
    output+=f'{msol.get_objective_values()[0]} {"{0:.3f}".format(total_time)}'
#print(output)

f = open(filename+'_titov_flag_'+str(flag)+'.out',"w+")
f.write(output)
f.close()
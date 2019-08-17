
import networkx as nx
from pulp import *


class Job(object):

    def __init__(self, Id, r, p):
        self.Id = Id
        self.r = r  # route
        self.p = p  # processing times

if __name__ == "__main__":
    jobs = {}
    jobs[1] = Job(1, [1, 2, 3], [10, 8, 4])
    jobs[2] = Job(2, [2, 1, 4, 3], [8, 3, 5, 6])
    jobs[3] = Job(3, [1, 2, 4], [4, 7, 3])


class Jobshop(nx.DiGraph):

    def __init__(self):  # , jobs):
        super().__init__()
        self.machines = {}
        self.add_node("U", p=0)
        self.add_node("V", p=0)

    def handleJobRoutings(self, jobs):
        for j in jobs.values():
            self.add_edge("U", (j.r[0], j.Id))
            for m, n in zip(j.r[:-1], j.r[1:]):
                self.add_edge((m, j.Id), (n, j.Id))
            self.add_edge((j.r[-1], j.Id), "V")

    def handleJobProcessingTimes(self, jobs):
        for j in jobs.values():
            for m, p in zip(j.r, j.p):
                self.add_node((m, j.Id), p=p)

    def makeMachineSubgraphs(self):
        machineIds = set(ij[0] for ij in self if ij[0] not in ("U", "V"))
        #print(machineIds)
        for m in machineIds:
            self.machines[m] = self.subgraph(ij for ij in self if ij[0] == m)
            #print(list(self.machines[m].nodes))
            #self.machines[m].remove_nodes_from(["U", "V"])

    def addJobs(self, jobs):
        self.handleJobRoutings(jobs)
        self.handleJobProcessingTimes(jobs)
        self.makeMachineSubgraphs()

    def output(self):
        for m in sorted(self.machines):
            for j in sorted(self.machines[m]):
                print("{}: {}".format(j, self.node[j]['C']))

if __name__ == "__main__":
    js = Jobshop()
    js.addJobs(jobs)

if __name__ == "__main__":
    prob = LpProblem("Job shop", LpMinimize)

if __name__ == "__main__":
    H = sum(js.node[j]['p'] for j in js)
    T = range(H + 1)

if __name__ == "__main__":
    x = LpVariable.dicts("x", [(ij, t)
                               for ij in js for t in T], 0, 1, cat=LpInteger)

if __name__ == "__main__":
    C = LpVariable.dicts("C", [ij for ij in js])
    for ij in js:
        prob += C[ij] == lpSum([t * x[(ij, t)] for t in T])

if __name__ == "__main__":
    prob += C["V"]

if __name__ == "__main__":
    for ij in js:
        prob += lpSum([x[(ij, t)] for t in T]) == 1

if __name__ == "__main__":
    for ij in js:
        prob += C[ij] >= js.node[ij]['p']

if __name__ == "__main__":
    for ij in js:
        for k in js. predecessors(ij):
            prob += C[ij] >= C[k] + js.node[ij]['p']

if __name__ == "__main__":
    p = lambda ij, t: lpSum([x[(ij, u)]
                             for u in range(t, t + js.node[ij]['p'])])

if __name__ == "__main__":
    for i in js.machines:
        for t in T:
            prob += lpSum([p(ij, t) for ij in js.machines[i]
                           if t <= H - js.node[ij]['p'] + 1]) <= 1

if __name__ == "__main__":
    # prob.solve(GLPK(msg=0))
    prob.solve()

    print("status", LpStatus[prob.status])
    print("objective", value(prob.objective))

    for j in js:
        for t in T:
            if x[j, t].varValue > 0:
                js.add_node(j, C=t)

    js.output()

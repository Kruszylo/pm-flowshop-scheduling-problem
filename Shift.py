#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 25 19:08:54 2018

@author: kruszylo
"""
from cpmGraph import CPM
from jobShopIP import Jobshop, Job
from itertools import permutations
import itertools as it
from tqdm import tqdm
def argmin_kv(d):
    return min(d.items(), key=lambda x: x[1])
  
def sorted_k_partitions(seq, k):
    """Returns a list of all unique k-partitions of `seq`.

    Each partition is a list of parts, and each part is a tuple.

    The parts in each individual partition will be sorted in shortlex
    order (i.e., by length first, then lexicographically).

    The overall list of partitions will then be sorted by the length
    of their first part, the length of their second part, ...,
    the length of their last part, and then lexicographically.
    """
    n = len(seq)
    groups = tuple()  # a list of lists, currently empty
    def generate_partitions(i):
        nonlocal groups
        
        if i >= n:
            yield groups
        else:
            if n - i > k - len(groups):
                for j in range(len(groups)):
#                     print(groups)
                    new_group=groups[j]+(seq[i],)
                    groups = groups[:j] + (new_group,) + groups[j+1:]
#                     print(groups)
                    yield from generate_partitions(i + 1)
#                     print(groups[j])
                    new_group=groups[j][:-1]
                    
                    groups = groups[:j] + (new_group,) + groups[j+1:]

            if len(groups) < k:
                groups=groups+((seq[i],),)
                
                yield from generate_partitions(i + 1)
                groups=groups[:-1]

    result = generate_partitions(0)
    #     print(type(result))
    # Sort the parts in each partition in shortlex order
    #     result = [sorted(ps, key = lambda p: (len(p), p)) for ps in result]
    # Sort partitions by the length of each part, then lexicographically.
    #     result = sorted(result, key = lambda ps: (*map(len, ps), ps))

    return result

def get_partition(S,k):
    partitions = set()
    for i in (range(k)):
        for groups in sorted_k_partitions(S, k-i):
            for perm in it.permutations(groups+tuple(tuple() for j in range(i))):
                if perm not in partitions: 
                    partitions.add( perm )
                    yield perm
                
class Shift(Jobshop, CPM):
    def put_to_machine(self,identical_machines, i,j):
        added = False
        for mi, mtasks in identical_machines.items():
            if len(mtasks)>0:
                if mtasks[-1] == i:
                    identical_machines[mi].append(j)
                    added = True
                    break
        if not added: 
            min_l = float('inf')
            add_to_mi = -1
            for mi, mtasks in identical_machines.items():
                if len(mtasks)<min_l:
                    min_l, add_to_mi = len(mtasks), mi
            identical_machines[add_to_mi].append(i)
            return add_to_mi
        
    def print_table(self,machine):
        s = "{0:<7s}".format("jobs:")
        for ij in sorted(machine):
            if ij in ("U", "V"):
                continue
            s += "{0:>5d}".format(ij[1])
        print(s)
        s = "{0:<7s}".format("p:")
        for ij in sorted(machine):
            if ij in ("U", "V"):
                continue
            s += "{0:>5d}".format(self.node[ij]['p'])
        print(s)
        s = "{0:<7s}".format("r:")
        for ij in sorted(machine):
            if ij in ("U", "V"):
                continue
            s += "{0:>5d}".format(self.node[ij]['S'])
        print(s)
        s = "{0:<7s}".format("d:")
        for ij in sorted(machine):
            if ij in ("U", "V"):
                continue
            s += "{0:>5d}".format(self.node[ij]['Cp'])
        print(s)
        print("\n")
        
    def output(self):
        output = ''
#        print("makespan: ", self.makespan)
        for m in self.machines:
#            if self.identical_paralel_m > 1 and 0<=i<5:
#                pass
#            else:
            #print(f'm={m}')
            identical_machines = {i:list() for i in range(self.identical_paralel_m)}
            last_task = None
            for i in sorted(self.machines[m]):
                if i not in ("U", "V"):
                    for j in sorted(self.machines[m]):
                        if j not in ("U", "V"):
                            if self.has_edge(i, j):
                                add_to_mi = self.put_to_machine(identical_machines, i,j)
                                #print(i,j)
                                last_task = (add_to_mi, j)
            identical_machines[last_task[0]].append(last_task[1])
            ordered_tasks = set(task for tasks in identical_machines.values() for task in tasks)
            not_ordered_tasks = set(self.machines[m]) - ordered_tasks
            for task in not_ordered_tasks:
                for mi in identical_machines.keys():
                    if identical_machines[mi] == list():
                        identical_machines[mi].append(task)
                        break
            #print(identical_machines)
            for mi, machine in identical_machines.items():
                if mi > 0:
                    output += "M"+str(m)+'-'+str(mi)
                else:
                    output += "M"+str(m)+' '*len(identical_machines)
                #self.print_table(machine)
                sorted_by_r_tasks = sorted([self.node[task] for task in machine], key=lambda t: t['S'])
                s = ''
                for task in sorted_by_r_tasks:
                    for node in machine:
                        if self.node[node] == task:
                            s += f" {node[1]} {task['S']}"
                output += s + '\n'
        return output
            
    def branch_bound(self, head, nodes, min_Lmax):
        if len(nodes)<=2:
            rest_dd = [self.node[j]['Cp'] for j in nodes]
            rest_dict = {nodes[i]:rest_dd[i] for i in range(len(nodes))}
            di = [(dd[0][0],dd[0][1],dd[1]) for dd in list(rest_dict.items())]
            di.sort(key=lambda r: r[1])
            di.sort(key=lambda r: r[2], reverse=False)
            seq = [((ddi[0],ddi[1]),ddi[2]) for ddi in di]
            seq = head + [s[0] for s in seq]
            release = [self.node[j]['S'] for j in seq]
            due = [self.node[j]['Cp'] for j in seq]
            finish = [0]*len(release)
            for i, j in enumerate(seq):
                finish[i] = max(finish[i-1], release[i]) +self.node[j]['p']
#            print(f'finish={finish}')
#            print(f'due   ={due}')
            late = max([f-d for d,f in zip(due,finish)], default=0)
            
            return tuple(n for n in seq), max(0,late)
        lateness = {}
        for node in nodes:
            #create seq for each first node by Preemptive (EDD) rule
            rest_nodes = nodes.copy()
            rest_nodes.remove(node)
            rest_dd = [self.node[j]['Cp'] for j in rest_nodes]
            rest_dict = {rest_nodes[i]:rest_dd[i] for i in range(len(rest_nodes))}
            di = [(dd[0][0],dd[0][1],dd[1]) for dd in list(rest_dict.items())]
            di.sort(key=lambda r: r[1])
            di.sort(key=lambda r: r[2], reverse=False)
            seq = [((ddi[0],ddi[1]),ddi[2]) for ddi in di]
            seq = head + [node] + [s[0] for s in seq]
            release = [self.node[j]['S'] for j in seq]
            due = [self.node[j]['Cp'] for j in seq]
            finish = [0]*len(release)
            for i, j in enumerate(seq):
                finish[i] = max(finish[i-1], release[i]) +self.node[j]['p']
            late = max([f-d for d,f in zip(due,finish)], default=0)
            lateness[tuple(n for n in seq)] = late
        Lmax_seq, Lmax = argmin_kv(lateness)
        new_head_end = 1
        if len(head) > 0:
            new_head_end = Lmax_seq.index(head[0])+len(head)+1
        return self.branch_bound(list(Lmax_seq[:new_head_end]), list(Lmax_seq[new_head_end:]), Lmax)
            
    def computeLmax(self):
        #opt_m, opt_s, max_l = -1, [], -float('inf')
        m = self.slovest_machine_ind
        s, l = [], float('inf')
        
        if self.identical_paralel_m > 1 and 0<=m<5:
            #assuming that Machine indexes starts from 0 
            #check is m is one of those which has identical paralel copies:
            generator_of_tasks_partiton = get_partition(list(self.machines[m]),self.identical_paralel_m)
            tasks_partition = next(generator_of_tasks_partiton)
            total_num_of_perm = self.identical_paralel_m**len(self.machines[m])
            for perm_ind in tqdm(range(total_num_of_perm)):
#                print(f'tasks_partition={tasks_partition}')
                partition_Lmax = 0
                partition_s = []
                for tasks_sub_list in tasks_partition:
#                    print(f'tasks_sub_list={tasks_sub_list}')
                    sub_s, sub_l = self.branch_bound([], list(tasks_sub_list), float('inf'))
                    partition_Lmax += sub_l
                    partition_s.append(sub_s)
#                    print(sub_s)
#                    print(sub_l)
#                print(f'partition_Lmax={partition_Lmax}')
                if partition_Lmax <= 0:
#                    print(f'\npartition_Lmax={partition_Lmax}')
                    #feasible solution!
                    s, l = partition_s, partition_Lmax
                    break
                tasks_partition = next(generator_of_tasks_partiton, None)
            
        else:
            s, l = self.branch_bound([], list(self.machines[m]), float('inf'))
            s=[s]
        #if l > max_l:
        #   opt_m, opt_s, max_l = m, s, l
#        print("Machine: {}, lateness: {}, seq: {}".format(m, l, s))
        
#        print(f'CHOOSE MACHINE {m}')
        return m, s, l
  

import networkx as nx


class CPM(nx.DiGraph):

    def __init__(self):
        super().__init__()
        self._dirty = True
        self._makespan = -1
        self._criticalPath = None
        self.setted_up_machines = set()
        self.identical_paralel_m = 1
        self.slovest_machine_ind = -1
        self.machines_req_times = dict()

    def add_node(self, *args, **kwargs):
        self._dirty = True
        super().add_node(*args, **kwargs)

    def add_nodes_from(self, *args, **kwargs):
        self._dirty = True
        super().add_nodes_from(*args, **kwargs)

    def add_edge(self, *args):  # , **kwargs):
        self._dirty = True
        super().add_edge(*args)  # , **kwargs)

    def add_edges_from(self, *args, **kwargs):
        self._dirty = True
        super().add_edges_from(*args, **kwargs)

    def remove_node(self, *args, **kwargs):
        self._dirty = True
        super().remove_node(*args, **kwargs)

    def remove_nodes_from(self, *args, **kwargs):
        self._dirty = True
        super().remove_nodes_from(*args, **kwargs)

    def remove_edge(self, *args):  # , **kwargs):
        self._dirty = True
        super().remove_edge(*args)  # , **kwargs)

    def remove_edges_from(self, *args, **kwargs):
        self._dirty = True
        super().remove_edges_from(*args, **kwargs)

    def _forward(self):
        for n in nx.topological_sort(self):
#            print(f'FORWARD: {[self.node[j] for j in self.predecessors(n)]}')
            S = max([self.node[j]['C']
                     for j in self.predecessors(n)], default=0)
            self.add_node(n, S=S, C=S + self.node[n]['p'])

    def _backward(self):
        for n in reversed(list(nx.topological_sort(self))):#, reverse=True):
#            print([self.node[j] for j in self.successors(n) if 'Sp' in self.node[j]])
#            Cp = min([self.node[j]['Sp']
#                      for j in self.successors(n) if 'Sp' in self.node[j]], default=self._makespan)
#            print(f'self.node[n]={self.node[n]}, n={n}')
#            print(f'BACKWARD: {[(j,self.node[j]) for j in self.successors(n) ]}')
#            if n[0] == self.slovest_machine_ind:
            Cp = min([self.node[j]['Sp']
                      for j in self.successors(n)], default=self._makespan)
#            print(f'Cp={Cp}, Sp={Cp - self.node[n]["p"]}')
            self.add_node(n, Sp=Cp - self.node[n]['p'], Cp=Cp)

    def _computeCriticalPath(self):
        G = set()
        for n in self:
            if self.node[n]['C'] == self.node[n]['Cp']:
                G.add(n)
        self._criticalPath = self.subgraph(G)

    @property
    def makespan(self):
        if self._dirty:
            self._update()
        return self._makespan

    @property
    def criticalPath(self):
        if self._dirty:
            self._update()
        return self._criticalPath

    def _update(self):
        self._forward()
        self._makespan = max(nx.get_node_attributes(self, 'C').values())
        self.machines_req_times = {i:0 for i in set(n[0] for n in self if n not in ['U', 'V'])}
        
        for n in self:
            if n not in ['U', 'V'] and n[0] not in self.setted_up_machines:
              self.machines_req_times[n[0]] += self.node[n]['p']  
        #print(f'machines_req_times: {machines_req_times}')
        self.slovest_machine_ind = max(self.machines_req_times, key=self.machines_req_times.get)
        print(f'slowest_machine_ind: {self.slovest_machine_ind}')
        self._makespan = max(max(self.machines_req_times.values()),self._makespan)
        self._backward()
        self._computeCriticalPath()
        self._dirty = False


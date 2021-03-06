from typing import List, Union
import numpy as np

import scipy.sparse

## statistics

from .project import Project


def max_time(project: Project):
    max_t = project.best_before + project.max_score
    return max_t

def max_runtime(problem: 'problem.Problem'):
    time = []
    for proj in problem.projects:
        time.append(max_time(proj))
    return max(time)

def min_timestep(problem: 'problem.Problem'):
    time = []
    for proj in problem.projects:
        time.append(proj.days_to_complete)
    return min(time)

def get_unique_skills(problem: 'problem.Problem'):
    unique_skills = set()
    for w in problem.workers:
        unique_skills.update(w.skills.keys())
    for pr in problem.projects:
        unique_skills.update(pr.roles)
    return unique_skills

def level_needed_per_skill(problem: 'problem.Problem'):
    lvl_per_skill = {}
    for u_skill in get_unique_skills(problem):
        level = 0
        for pr in problem.projects:
            try:
                index = pr.roles.index(u_skill)
                lvl = pr.levels[index]
                if lvl > level:
                    level = lvl
                    lvl_per_skill.update({u_skill:level})
            except:
                pass
    return lvl_per_skill

def max_level_per_skill(problem):
    lvl_per_skill = {}
    for u_skill in get_unique_skills(problem):
        level = 0
        for w in problem.workers:
            try:
                lvl = w.skills[u_skill]
                if lvl > level:
                    level = lvl
                    lvl_per_skill.update({u_skill:level})
            except:
                pass
    return lvl_per_skill
#################################
#   List of List <-> Matrix     #
#################################

def unique_entries(lol):
    """ Gives the unique entries in one list of list """
    uniques = set()
    for l in lol:
        uniques.update(l)
    return uniques


def unique_entries_multiple(*lols):
    """ Gives the unique entries in multiple list of lists """
    uniques = set()
    for lol in lols:
        uniques.update(unique_entries(lol))
    return uniques


def list_of_lists_to_matrix(lol, uniques: List):
    """ Converts a list of lists to a matrix representation with columns equal to uniques.
    Returns matrix and uses uniques as columns """
    uniques_index = {k: i for i, k in enumerate(uniques)}
    m, n = len(lol), len(uniques)

    row_index = list()
    col_index = list()
    for col, l in enumerate(lol):
        indices = [uniques_index[k] for k in l]
        col_index.extend(indices)
        row_index.extend([col] * len(indices))

    data = np.ones(len(row_index))
    # print(data)
    # print(row_index)
    # print(col_index)
    return scipy.sparse.csr_matrix((data, (row_index, col_index)), shape=(m, n))


def vector_to_list(v, uniques):
    """ Converts a single binary vector back to a list of items according to index of uniques """
    indices = v.nonzero()[0]
    return [uniques[i] for i in indices]


#################
#   Graphs      #
#################

from graphviz import Digraph


class Graph:
    def __init__(self):
        self.nodes = dict()

    def addNode(self, name):
        """ Force add node """
        assert name not in self.nodes
        self.nodes[name] = Node(self, name)

    def getNode(self, name):
        """ Get or create node. """
        if name not in self.nodes:
            self.nodes[name] = Node(self, name)
        return self.nodes[name]

    def __str__(self):
        return "\n".join([str(node) for node in self.nodes.values()])

    def toDot(self):
        # other shape: plaintext
        dot = Digraph(node_attr={'shape': 'circle'})
        for node in self.nodes.values():
            node.toDot(dot)
        return dot


class Node:
    def __init__(self, graph: Graph, name: str):
        self.graph = graph
        self.name = name
        # edges pointing away from node (reading allowed, for writing use functions)
        self.outgoing = dict()
        # edges pointing to node (reading allowed, for writing use functions)
        self.incoming = dict()

    def addOutgoing(self, node: Union[str, 'Node'], data=None):
        if isinstance(node, str):
            node = self.graph.getNode(node)
        if not node in self.outgoing:
            self.outgoing[node] = data
            node.addIncoming(self, data)

    def addIncoming(self, node: Union[str, 'Node'], data=None):
        if isinstance(node, str):
            node = self.graph.getNode(node)
        if not node in self.incoming:
            self.incoming[node] = data
            node.addOutgoing(self, data)

    def __str__(self):
        s = self.name + '\n'
        for node, edge in self.outgoing.items():
            s += f"->{node.name} ({repr(edge)})\n"
        for node, edge in self.incoming.items():
            s += f"<-{node.name} ({repr(edge)})\n"
        return s

    def toDot(self, dot):
        dot.node(self.name)
        for other, data in self.outgoing.items():
            dot.edge(self.name, other.name, str(data))


from src import problem

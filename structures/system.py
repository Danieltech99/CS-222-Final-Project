import numpy as np
import matplotlib.pyplot as plt


# nodes for storing information
class Node(object):

    def __init__(self, init_state):

        self._prev_state = init_state
        self._next_state = init_state

    # store the state update
    def update(self, update):
        self._next_state += update

    # store the state update
    def set(self, update):
        self._next_state = update

    # push the state update
    def step(self):
        self._prev_state = self._next_state

    @property
    def state(self):
        return self._prev_state


# Graph for connecting nodes
class Graph(object):

    def __init__(self, node_list, adj_matrix):

        self.node_list = node_list
        self.adj_matrix = adj_matrix

        self._finished = False      

    # update the graph
    def update_graph(self):
        raise NotImplementedError

    # return the state of the nodes currently - you can disable print here
    def node_states(self):
        string = ""
        out = []
        for node in self.node_list:
            string = string + str(node.state) + "\t"
            out.append(node.state)
        # print(string)

        return out

    # check if the graph has reached consensus somehow, even if there are adversaries
    def is_finished(self):
        raise NotImplementedError

    @property
    def finished(self):
        # add your code here
        return self._finished



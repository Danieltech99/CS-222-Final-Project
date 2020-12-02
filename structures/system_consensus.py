import numpy as np
import matplotlib.pyplot as plt
from structures.system import Node as NodeBase, Graph as GraphBase


# nodes for storing information
class Node(NodeBase):

    def __init__(self, *args):
        super().__init__(*args)


# Graph for connecting nodes
class Graph(GraphBase):

    def __init__(self, node_list, adj_matrix, epsilon = 0.2, threshold = 0):

        self.node_list = node_list
        self.adj_matrix = adj_matrix

        self._epsilon = epsilon

        self._finished = False      # bool determining when we've reached a threshold
        self._threshold = threshold

    # update the graph
    def update_graph(self):

        # For each robot
        for bot_i, bot in enumerate(self.node_list):
            total = 0
            # ... go through each of its neighbors
            for n_i, neighbor in enumerate(self.node_list):
                # ... if not connection/edge with neighbor then skip
                if not self.adj_matrix[bot_i][n_i]: continue

                # ... Calcute the difference between 
                # ... the neighbor state and the robot state
                value = (neighbor.state - bot.state)

                
                # ... multiply value by the weight of the edge
                # ... (note that because of this line the above if is not needed
                # ... but the above if prevents unnecessary work)
                total += self.adj_matrix[bot_i][n_i] * value
            
            # Moltiply the total difference by epsilon and send to robot
            bot.update(total * self._epsilon)

        # Loop over all robots and step after all the updates have been set
        # (Simulated synchronicity)
        for bot in self.node_list:
            bot.step()
        
        # Not used but checks if consensus of all bots are within epsilon
        self.is_finished()

    # check if the graph has reached consensus somehow, even if there are adversaries
    def is_finished(self):
        # Checks if consensus of all bots are within epsilon

        # Max robot state
        top = max([node.state for node in self.node_list])
        # Min robot state
        bottom = min([node.state for node in self.node_list])
        # Difference between max and min robot state
        diff = abs(top - bottom)
        # Returns true if difference is within epsilon
        self._finished = diff <= self._epsilon

    @property
    def finished(self):
        # add your code here
        return self._finished



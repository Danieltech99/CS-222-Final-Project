import numpy as np
import copy

from algorithms.runtime import Leader, Node

# BE CAREFUL: after removing a node, the indices change

class EnvironmentConnections():
    def __init__(self, graph, nodes):
        # Assign nodes ids for removals and additions
        assert(len(nodes) == len(graph))
        for i in range(len(nodes)):
            nodes[i].id = i
        if len(nodes) > 1: assert(nodes[0].id != nodes[1].id)
        self.ordered_ids = [node.id for node in nodes]
        self.node_dict = {node.id:node for node in nodes}
        
        # Represents environment conditions of connections
        self.g = graph
    
    # Administrative Public Methods
    def add_node_to_environment(self,node_obj):
        # Does not add to flock or adjacency matrix
        # AFTER: use `add_node`
        assert(node_obj.id not in self.node_dict)
        self.node_dict[node_obj.id] = node_obj
        return self
    def remove_node_from_environment(self,node_obj):
        # Does not remove from flock or adjacency matrix
        # FIRST: use `remove_node`
        assert(node_obj.id in self.node_dict)
        assert(node_obj.id not in self.ordered_ids)
        del self.node_dict[node_obj.id]
        return self
    def get_id(self, node_index):
        return self.ordered_ids[node_index]
    
    # Private Methods
    def get_index(self, node_id):
        return self.ordered_ids.index(node_id)
    
    # Main Public Methods
    def remove_edge(self,u_id,v_id):
        assert(u_id in self.ordered_ids)
        assert(v_id in self.ordered_ids)
        u, v = self.get_index(u_id), self.get_index(v_id)
        self.g[u][v] = 0
        self.g[v][u] = 0
        return self
    def remove_edges(self,edges):
        for (u_id,v_id) in edges:
            self.remove_edge(u_id,v_id)
        return self
    def remove_node(self, node_id):
        assert(node_id in self.ordered_ids)
        node_index = self.get_index(node_id)
        self.g = np.delete(self.g, node_index, 0)
        self.g = np.delete(self.g, node_index, 1)
        self.ordered_ids.pop(node_id)
        return self
    def add_edge(self, u_id,v_id, w = 1):
        assert(u_id in self.ordered_ids)
        assert(v_id in self.ordered_ids)
        u, v = self.get_index(u_id), self.get_index(v_id)
        self.g[u][v] = w
        self.g[v][u] = w
        return self
    def add_edges(self,edges, w = 1):
        for (u_id,v_id) in edges:
            self.add_edge(u_id,v_id)
        return self
    def add_node(self, node_id, at_index):
        assert(node_id not in self.ordered_ids)
        self.g = np.insert(self.g, at_index, 0, axis=1)
        self.g = np.insert(self.g, at_index, 0, axis=0)
        self.ordered_ids.insert(at_index, node_id)
        return self
    def add_all_edges(self, node_id, w = 1):
        assert(node_id in self.ordered_ids)
        l = len(self.g)
        for id in self.ordered_ids:
            if node_id != id:
                self.add_edge(node_id, id)
        return self
    # def eject(self):
    #     return self.g

class CommunicationWrapper():
    def __init__(self, env_communications, leader_id, current_id):
        self._connections = env_communications
        self._leader_id = leader_id
        self._current_id = current_id
    
    def get_neighbors(self):
        node_id = self._current_id
        node_index = self._connections.get_index(node_id)
        g_id = self._connections.get_id
        neighbors_indexes = [i for i,w in enumerate(self._connections.g[node_index]) if w and i != node_index]
        neighbors_nodes = [self._connections.node_dict[g_id(i)] for i in neighbors_indexes]
        return neighbors_nodes
    
    # Leader to follower communication
    # Assumes leader algorithm and leader election algorithm in place
    # Leader can propogate a command to everyone
    # Only connected in flock
    def get_all_followers(self):
        assert(self._leader_id == self._current_id)
        connected_ids = [id for id in self._connections.ordered_ids if id != self._leader_id]
        return [self._connections.node_dict[id] for id in connected_ids]

    # Assume leader has some way of getting flock adj amtrix
    def leader_request_adj_matrix(self):
        assert(self._leader_id == self._current_id)
        return self._connections.g

    # General communication
    # Assumes leader algorithm and leader election algorithm in place
    # Follower can always communicate to leader
    def get_leader(self):
        return self._connections.node_dict[self._leader_id]


class Environment():
    def __init__(self,graph,runtime_alg):
        nodes = [Node(i) for i in range(len(graph))]
        self.leader = Leader(0)
        nodes[0] = self.leader
        self.leader.set_alg(runtime_alg)
        self.connections = EnvironmentConnections(graph, nodes)
        for node in nodes:
            # Sets first node as leader
            node.communications = CommunicationWrapper(self.connections, nodes[0].id, node.id)
    
    def perform_time_step(self, f):
        self.connections = f(self.connections)
        return self.leader.leader_update()
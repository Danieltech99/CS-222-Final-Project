import numpy as np
import copy



class Node():
    id = None
    communications = None
    def __init__(self, id):
        self.last_neighbor_ids = set()
        self.neighbor_ids = set()

    def get_neighbors(self):
        self.last_neighbor_ids = self.neighbor_ids.copy()
        neighbor_nodes = self.communications.get_neighbors()
        self.neighbor_ids = set(node.id for node in neighbor_nodes)

    noticed_added_edge = False
    noticed_missing_edge = False
    def reset(self):
        self.noticed_added_edge = False
        self.noticed_missing_edge = False

    def compare_neighbors(self):
        if self.neighbor_ids - self.last_neighbor_ids:
            self.noticed_added_edge = True
        if self.last_neighbor_ids - self.neighbor_ids:
            self.noticed_missing_edge = True

    def update(self):
        self.get_neighbors()
        self.compare_neighbors()
        leader = self.communications.get_leader()
        if self.noticed_missing_edge:
            leader.follower_noticed_missing_edge = True
        if self.noticed_added_edge:
            leader.follower_noticed_added_edge = True


class Leader(Node):
    follower_noticed_missing_edge = False
    follower_noticed_added_edge = False

    leader_detected_missing_node = False
    leader_detected_new_node = False

    def __init__(self, *args):
        super().__init__(*args)
        self.last_follower_ids = set()
        self.follower_ids = set()

    def get_followers(self):
        self.last_follower_ids = self.follower_ids.copy()
        self.follower_nodes = self.communications.get_all_followers()
        self.follower_ids = set(node.id for node in self.follower_nodes)
    
    def compare_followers(self):
        if self.follower_ids - self.last_follower_ids:
            self.leader_detected_new_node = True
        if self.last_follower_ids - self.follower_ids:
            self.leader_detected_missing_node = True

    def leader_reset(self):
        self.follower_noticed_missing_edge = False
        self.follower_noticed_added_edge = False
        self.leader_detected_missing_node = False
        self.leader_detected_new_node = False
        for node in self.follower_nodes:
            node.reset()

    def set_alg(self,alg):
        self.alg = alg

    def leader_update(self):
        self.get_followers()
        self.compare_followers()
        for node in self.follower_nodes:
            node.update()
        adj_matrix = self.communications.leader_request_adj_matrix()

        added_node = self.leader_detected_new_node
        added_edge = self.follower_noticed_added_edge
        missing_node = self.leader_detected_missing_node
        missing_edge = self.follower_noticed_missing_edge

        results = self.alg.perform(adj_matrix, added_node, added_edge, missing_node, missing_edge)
        
        self.leader_reset()
        return results



class Runtime():
    name = "Runtime (Reset)"
    def __init__(self, specify_alg):
        self.specify_alg = specify_alg
    def perform(self, adj_matrix, added_node, added_edge, missing_node, missing_edge):
        return self.specify_alg(adj_matrix)

class RuntimeResidualAddativeEdges(Runtime):
    name = "Runtime (Residual Add Edges)"
    residual = None
    last_full_matrix = None
    allow_print = False

    def perform(self, adj_matrix, added_node, added_edge, missing_node, missing_edge):
        source_matrix = adj_matrix
        
        degrading_or_transformative = missing_edge or missing_node or added_node
        memory_set = self.residual is not None and self.last_full_matrix is not None

        # If not degrading_or_transformative,
        # ... then edges have been added
        if memory_set and not degrading_or_transformative:
            # Find common edges between this adj matrix and last adj matrix
            math_diff = np.multiply(adj_matrix,self.last_full_matrix)
            # Remove common edges from this adj matrix to get only added edges
            math_diff = adj_matrix - math_diff
            
            # Use diff to get all new edges and add those to residual for alg
            source_matrix = self.residual + math_diff
        else:
             # Node was addded or removed
            # ... meaning dim of flock has changed
            # ... OR edge was removed
            # ... thus reset
            if self.allow_print: 
                print("\t\t\t {} is not using residual".format(self.name))
        
        # Feed either the full graph (reset) or the residual graph to the alg
        result_graph = self.specify_alg(source_matrix)
        
        # Save to memory
        self.residual = copy.deepcopy(result_graph)
        self.last_full_matrix = copy.deepcopy(adj_matrix)

        # Return results
        return result_graph

class RuntimeResidual(RuntimeResidualAddativeEdges):
    name = "Runtime (Residual Add/Remove Edges)"

    def perform(self, adj_matrix, added_node, added_edge, missing_node, missing_edge):
        source_matrix = adj_matrix
        
        # Allow missing edges (compared to RuntimeResidualAddativeEdges)
        transformative = missing_node or added_node
        memory_set = self.residual is not None and self.last_full_matrix is not None
        
        # If missing edge not in residual
        if memory_set and not transformative:
            # Take intersection to find edges in full graph and residual
            intersection = np.multiply(adj_matrix,self.residual)
            # Make sure intersection is same as residual
            # ... which means no edges in the residual have been removed
            missing_not_in_residual = np.array_equal(intersection,self.residual)
            # If no edges in the residual have been removed, we can use the residual
            if missing_not_in_residual:
                # Find common edges between this adj matrix and last adj matrix
                math_diff = np.multiply(adj_matrix,self.last_full_matrix)
                # Remove common edges from this adj matrix to get only added edges
                math_diff = adj_matrix - math_diff
                
                # Use diff to get all new edges and add those to residual for alg
                source_matrix = self.residual + math_diff
            else:
                # Edge from residual was removed, thus reset
                if self.allow_print:
                    print("\t\t\t {} is not using residual".format(self.name))
                pass
        else:
            # Node was addded or removed
            # ... meaning dim of flock has changed
            # ... thus reset
            if self.allow_print:
                print("\t\t\t {} is not using residual".format(self.name))
            pass
        
        # Feed either the full graph (reset) or the residual graph to the alg
        result_graph = self.specify_alg(source_matrix)

        # Save to memory
        self.residual = copy.deepcopy(result_graph)
        self.last_full_matrix = copy.deepcopy(adj_matrix)

        # Return results
        return result_graph




    

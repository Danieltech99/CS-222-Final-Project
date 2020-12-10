class IdManager():
    def __init__(self, adj_matrix, nodes):
        # Assign nodes ids for removals and additions
        assert(len(nodes) == len(adj_matrix))
        for i in range(len(nodes)):
            nodes[i].id = i + 1
        if len(nodes) > 1: assert(nodes[0].id != nodes[1].id)
        self.ordered_ids = [node.id for node in nodes]
        self.node_dict = {node.id:node for node in nodes}
    
    def get_id(self, node_index):
        return self.ordered_ids[node_index]
    
    # Private Methods
    def get_index(self, node_id):
        return self.ordered_ids.index(node_id)
import time

packet_id_inc = 1
class Packet():
    type = "packet"
    def __init__(self, data, source_id, target_id):
        global packet_id_inc
        self.id = packet_id_inc
        packet_id_inc += 1

        self.created_at = time.time()
        self.data = data

        self.source_id = source_id
        self.target_id = target_id
    
    # Can also be switched to time in transit 
    # ... (sum of time being communicated, not including processing)
    hops = 0
    def inc(self, weight = 1):
        self.hops += weight

    def clone(self):
        packet_copy = Packet(self.data, self.source_id, self.target_id)
        packet_copy.hops = self.hops
        return packet_copy

class PacketMeta():
    type = "meta"
    def __init__(self, packet, from_id, to_id):
        self.packet = packet
        self.from_id = from_id
        self.to_id = to_id
    
    def unwrap(self):
        return self.packet

class ACK(Packet):
    type = "ack"
    def __init__(self, p_id):
        self.id = p_id

class Node():
    def __init__(self):
        self.in_queue = []

class IdManager():
    def __init__(self, adj_matrix, nodes):
        # Assign nodes ids for removals and additions
        assert(len(nodes) == len(adj_matrix))
        for i in range(len(nodes)):
            nodes[i].id = i
        if len(nodes) > 1: assert(nodes[0].id != nodes[1].id)
        self.ordered_ids = [node.id for node in nodes]
        self.node_dict = {node.id:node for node in nodes}
    
    def get_id(self, node_index):
        return self.ordered_ids[node_index]
    
    # Private Methods
    def get_index(self, node_id):
        return self.ordered_ids.index(node_id)

class DirectCommunication(IdManager):
    packets_sent = 0
    def __init__(self, adj_matrix, current_id, manager):
        self.manager = manager
        self.adj_matrix = adj_matrix
        self._current_id = current_id

    def send(self, node_id, packet):
        assert(node_id != self._current_id)
        u, v = self.manager.get_index(self._current_id), self.manager.get_index(node_id)
        if self.adj_matrix[u][v]:
            self.packets_sent += 1
            # HAVE TO CLONE to keep hops accurate.
            packet = packet.clone()
            # Time to travel is inverse of weight
            packet.inc(self.adj_matrix[u][v]) # Inc hops proportional to weight of edge
            self.manager.node_dict[node_id].in_queue.append(PacketMeta(packet, self._current_id, node_id))
        
    def get_neighbor_ids(self):
        node_index = self.manager.get_index(self._current_id)
        # Get edges
        neighbors_indexes = [i for i,w in enumerate(self.adj_matrix[node_index]) if w and i != node_index]
        # Return ids for edges
        neighbors_ids = [self.manager.get_id(i) for i in neighbors_indexes]
        return neighbors_ids

class BroadcastNode():
    id = None
    packets_processed = 0
    packets_sent = 0
    def __init__(self):
        self.in_queue = []
        # Format {target_id: (route_node, route_hops)}
        self.route_t = {}

    def set_communicator(self,communicator):
        self.com = communicator

    def process(self):
        self.packets_processed += len(self.in_queue)
        while len(self.in_queue):
            packet_meta = self.in_queue.pop(0)
            packet = packet_meta.unwrap()
            if (packet.source_id == self.id):
                # Dont resend or update table for own packet
                pass
            elif (packet.source_id not in self.route_t or
                self.route_t[packet.source_id][1] > packet.hops):
                self.route_t[packet.source_id] = (packet_meta.from_id, packet.hops)
                
                # Arrived
                if packet.target_id == self.id:
                    # Terminate
                    pass
                else:
                    # Rebroadcast in case shorter for others (inspiration Dijkstra)
                    for neighbor in self.com.get_neighbor_ids():
                        # don't send back to sender
                        if neighbor != packet_meta.from_id:
                            self.packets_sent += 1
                            self.com.send(neighbor, packet)
                
            else:
                # Already recieved packet and slower path
                pass
                
    def broadcast(self):
        for neighbor in self.com.get_neighbor_ids():
            # Broadcast empty packet with no destination
            self.packets_sent += 1
            self.com.send(neighbor, Packet(None, self.id, None))

    def setup(self):
        self.broadcast()
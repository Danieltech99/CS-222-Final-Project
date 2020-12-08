import time
import bisect 
import numpy as np

from structures.id_manager import IdManager


packet_id_inc = 1
class Packet():
    type = "packet"
    def __init__(self, data, source_id, target_id):
        global packet_id_inc
        self.id = packet_id_inc
        packet_id_inc += 1

        # self.created_at = time.time()
        self.data = data

        self.source_id = source_id
        self.target_id = target_id
    
    # Can also be switched to time in transit 
    # ... (sum of time being communicated, not including processing)
    t_in_transit = 0
    def inc(self, weight = 1):
        self.t_in_transit += weight

    def clone(self):
        packet_copy = Packet(self.data, self.source_id, self.target_id)
        packet_copy.t_in_transit = self.t_in_transit
        return packet_copy

class PacketMeta():
    type = "meta"
    def __init__(self, packet, from_id, to_id):
        self.packet = packet
        self.from_id = from_id
        self.to_id = to_id
        # Meta assigned by env and includes when the packet arrives
        # according to when sent and link weight
        
    def set_arrival(self, time_of_arrival):
        self.time_of_arrival = time_of_arrival
    
    def __lt__(self, other):
        # For bisect
        return self.time_of_arrival < other.time_of_arrival

    def unwrap(self):
        return self.packet

class Node():
    def __init__(self):
        # in queue handled by environment
        pass


class TimedEnvironment():
    packet_queue = []
    time = 0
    def __init__(self, manager):
        self.manager = manager

    def run(self):
        packet_meta = self.packet_queue.pop(0)
        # fast forward time until time of next arrival
        self.time = packet_meta.time_of_arrival
        self.manager.node_dict[packet_meta.to_id].process(packet_meta)

    def queue(self, packet_meta, time_in_travel):
        packet_meta.set_arrival(time_in_travel + self.time)
        bisect.insort(self.packet_queue, packet_meta)


class TimedNeighborCommunication(IdManager):
    packets_sent = 0
    def __init__(self, adj_matrix, current_id, manager, env):
        self.manager = manager
        self.env = env
        self.adj_matrix = adj_matrix
        self._current_id = current_id

    def send(self, node_id, packet):
        assert(node_id != self._current_id)
        u, v = self.manager.get_index(self._current_id), self.manager.get_index(node_id)
        if self.adj_matrix[u][v]:
            self.packets_sent += 1
            # HAVE TO CLONE to keep t_in_transit accurate.
            packet = packet.clone()
            # Higher weight means more travel time
            time_in_travel = self.adj_matrix[u][v]
            packet.inc(time_in_travel) # Inc t_in_transit proportional to weight of edge
            self.env.queue(PacketMeta(packet, self._current_id, node_id), time_in_travel)
        
    def get_neighbor_ids(self):
        node_index = self.manager.get_index(self._current_id)
        # Get edges
        neighbors_indexes = [i for i,w in enumerate(self.adj_matrix[node_index]) if w and i != node_index]
        # Return ids for edges
        neighbors_ids = [self.manager.get_id(i) for i in neighbors_indexes]
        return neighbors_ids

class TimedBroadcastNode():
    id = None
    packets_processed = 0
    packets_sent = 0
    def __init__(self):
        # in queue handled by environment
        # Format {target_id: (route_node, route_t_in_transit)}
        self.route_t = {}

    def set_communicator(self,communicator):
        self.com = communicator

    def process(self, packet_meta):
        # environment gives packet, instead of agent requesting
        packet = packet_meta.unwrap()
        if (packet.source_id == self.id):
            # Dont resend or update table for own packet
            pass
        elif (packet.source_id not in self.route_t or
            self.route_t[packet.source_id][1] > packet.t_in_transit):
            self.route_t[packet.source_id] = (packet_meta.from_id, packet.t_in_transit)
            
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
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

        self.created_at = time.time()
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
        packet_copy.created_at = self.created_at
        packet_copy.t_in_transit = self.t_in_transit
        packet_copy.local_timestamp = self.local_timestamp
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




class TimedEnvironment():
    packet_queue = []
    time = 0
    def __init__(self, adj_matrix, manager):
        self.manager = manager
        self.adj_matrix = adj_matrix

    def run(self):
        packet_meta = self.packet_queue.pop(0)
        # fast forward time until time of next arrival
        self.time = packet_meta.time_of_arrival
        # print("moving", packet_meta.to_id, packet_meta.from_id, packet_meta.packet.data)
        self.manager.node_dict[packet_meta.to_id].process(packet_meta)
    
    def detect(self):
        # No packets recieved here, but work done so increment clock
        self.time += 1
        for bot in self.manager.node_dict.values():
            bot.detect()
        # print("finished detect", len(self.packet_queue), [p.packet.type for p in self.packet_queue])

    def queue(self, packet_meta, time_in_travel):
        packet_meta.set_arrival(time_in_travel + self.time)
        bisect.insort(self.packet_queue, packet_meta)


class TimedNeighborCommunication(IdManager):
    packets_sent = 0
    def __init__(self, current_id, manager, env):
        self.manager = manager
        self.env = env
        self._current_id = current_id

    def send(self, node_id, packet):
        assert(node_id != self._current_id)
        u, v = self.manager.get_index(self._current_id), self.manager.get_index(node_id)
        assert(self.env.adj_matrix[u][v] > 0)
        if self.env.adj_matrix[u][v]:
            self.packets_sent += 1
            # HAVE TO CLONE to keep t_in_transit accurate.
            packet = packet.clone()
            # Higher weight means more travel time
            time_in_travel = self.env.adj_matrix[u][v]
            packet.inc(time_in_travel) # Inc t_in_transit proportional to weight of edge
            self.env.queue(PacketMeta(packet, self._current_id, node_id), time_in_travel)
        
    def get_neighbor_ids(self):
        node_index = self.manager.get_index(self._current_id)
        # Get edges
        neighbors_indexes = [(i,w) for i,w in enumerate(self.env.adj_matrix[node_index]) if w and i != node_index]
        # Return ids for edges
        neighbors_ids = [(self.manager.get_id(i),w) for i,w in neighbors_indexes]
        return neighbors_ids

class DynamicTimedEnvironment(TimedEnvironment):
    # Main Data Public Methods
    def remove_edge(self, u, v):
        self.adj_matrix[u][v] = 0
        self.adj_matrix[v][u] = 0
        return self
    def remove_edges(self, edges):
        for (u,v) in edges:
            self.remove_edge(u,v)
        return self
    def remove_all_edges(self, node_index):
        for id in range(len(self.adj_matrix)):
            if node_index != id:
                self.remove_edge(node_index, id)
        return self
    def add_edge(self, u, v, w = 1):
        self.adj_matrix[u][v] = w
        self.adj_matrix[v][u] = w
        return self
    def add_edges(self, edges, w = 1):
        for (u,v) in edges:
            self.add_edge(u,v)
        return self
    def add_all_edges(self, node_index, w = 1):
        for id in range(len(self.adj_matrix)):
            if node_index != id:
                self.add_edge(node_index, id)
        return self



# Seperated for ease of coding/organization and seperation of concerns

class Node():
    id = None
    packets_processed = 0
    packets_sent = 0
    leader = []
    local_timestamp = 0
    def __init__(self, initial_flock_size):
        # in queue handled by environment
        # flock size for handling initial updates
        self.initial_flock_size = initial_flock_size
        # Format {target_id: (route_node, route_length, route_broadcast_timestamp)}
        self.route_t = {}
        # Format {node_id: (longest_shortest_path_length, timestamp)}
        self.flock_lsp = {}
    
    def set_communicator(self,communicator):
        self.com = communicator

    def forward(self, packet_meta, route_updated):
        packet = packet_meta.unwrap()
        # If target is None, then broadcast
        # Similar to 0.0.0.0
        if packet.target_id is None and route_updated:
            self.broadcast(packet, packet_meta)
        # Otherwise, forward according to shortest path in routing table
        elif packet.target_id:
            self.packets_sent += 1
            self.send(self.route_t[packet.target_id][0], packet)

    def send(self, neighbor, packet):
        if packet.source_id == self.id:
            packet.local_timestamp = self.local_timestamp
        self.com.send(neighbor, packet)
                
    def broadcast(self, packet, packet_meta = None, dont_send_to = []):
        # Send to all neighbors
        for neighbor,_ in self.com.get_neighbor_ids():
            # don't send back to sender
            if not packet_meta or neighbor != packet_meta.from_id:
                if neighbor not in dont_send_to:
                    self.packets_sent += 1
                    self.send(neighbor, packet)

    def refresh_neighbors(self):
        # Store only ids in set for easier comparison
        self.neighbor_ids = set(n for n,_ in self.com.get_neighbor_ids())
        self.neighbor_weights = {n:w for n,w in self.com.get_neighbor_ids()}
    
    def refresh_neighbors_history(self):
        self.last_neighbor_ids = self.neighbor_ids.copy()
        self.last_neighbor_weights = self.neighbor_weights.copy()

    def compare_neighbors(self):
        added = self.neighbor_ids - self.last_neighbor_ids
        removed = self.last_neighbor_ids - self.neighbor_ids
        intersection = self.last_neighbor_ids.intersection(self.neighbor_ids)
        # Create dict of weight changes, not including links that stayed the same
        updated = {self.neighbor_weights[id] - self.last_neighbor_weights[id] for id in intersection if self.neighbor_weights[id] - self.last_neighbor_weights[id] != 0}
        return added,removed,updated

    def setup(self):
        self.refresh_neighbors()
        self.refresh_neighbors_history()

        self.broadcast(Packet(None, self.id, None))



class TimedBroadcastNode(Node):

    def share_longest_shortest_path(self):
        has_routes_to = [o for o in self.route_t.items() if o[1][0] is not None]
        if len(list(has_routes_to)) == 0: return
        data = {
            "type": "lsp_update",
            "value": max(has_routes_to, key=lambda entry: entry[1][1])[1][1]
        }
        # Instantiate outside of loop
        # ... so that all have the same timestamp
        p = Packet(data, self.id, None)
        p.local_timestamp = self.local_timestamp
        self.flock_lsp[self.id] = (data["value"],p.created_at)
        for (t,(neighbor, r_time, r_timestamp)) in list(has_routes_to):
            if neighbor is not None:
                indv_packet = p.clone()
                indv_packet.target_id = t
                self.send(neighbor, indv_packet)

    def consider_routing_update(self, packet_meta):
        packet = packet_meta.unwrap()
        # Don't add self to routing table
        if (packet.source_id == self.id): return False
        # If not in routing table
        # or newer broadcast timestamp
        # or set to no route for same timesatmp
        # or this is a shorter route but same timestamp
        # print("conditionals")
        # print(packet.source_id not in self.route_t)
        # print(packet.source_id not in self.route_t or
        #         self.route_t[packet.source_id][2] < packet.local_timestamp)
        # print(packet.source_id not in self.route_t or
        #         self.route_t[packet.source_id][2] < packet.local_timestamp or
        #         (self.route_t[packet.source_id][0] is None and self.route_t[packet.source_id][2] == packet.local_timestamp))
        # print(packet.source_id not in self.route_t or
        #         self.route_t[packet.source_id][2] < packet.local_timestamp or
        #         (self.route_t[packet.source_id][0] is None and self.route_t[packet.source_id][2] == packet.local_timestamp) or
        #         (self.route_t[packet.source_id][1] > packet.t_in_transit and self.route_t[packet.source_id][2] == packet.local_timestamp))
        if (
                packet.source_id not in self.route_t or
                self.route_t[packet.source_id][2] < packet.local_timestamp or
                (self.route_t[packet.source_id][0] is None and self.route_t[packet.source_id][2] == packet.local_timestamp) or
                (self.route_t[packet.source_id][1] > packet.t_in_transit and self.route_t[packet.source_id][2] == packet.local_timestamp)
            ):
            # Update routing table
            # print("updating {} on vertex {}, was {}".format(packet.source_id, self.id, self.route_t.get(packet.source_id)))
            self.route_t[packet.source_id] = (packet_meta.from_id, packet.t_in_transit, packet.local_timestamp)
            
            # Tell all neighbors of updated shortest path
            has_routes_to = [o for o in self.route_t.items() if o[1] is not None]
            self.share_longest_shortest_path()
            return True
        return False

    def update_leader(self):
        # Recalculate self
        has_routes_to = [o for o in self.route_t.items() if o[1][0] is not None]
        if not len(has_routes_to):
            self.flock_lsp[self.id] = (0, time.time())
        else:
            self.flock_lsp[self.id] = (max(has_routes_to, key=lambda entry: entry[1][1])[1][1], time.time())

        slsp = min(lsp for (lsp, _) in self.flock_lsp.values())
        self.leader = [id for id,(lsp,_) in self.flock_lsp.items() if lsp == slsp]

    def process(self, packet_meta):
        # environment gives packet, instead of agent requesting
        packet = packet_meta.unwrap()
        route_updated = self.consider_routing_update(packet_meta)
            
        self.handle(packet, packet_meta)
        # Arrived
        if packet.target_id == self.id:
            # Terminate
            pass
        else:
            # Pass packet along 
            self.forward(packet_meta, route_updated)

    
    def broadcast_routing_table(self):
        table = self.route_t.copy()


    def handle_longest_shortest_path_update(self,packet, packet_meta):
        # Update if not in table or if update created later in time
        if (packet.source_id == self.id): return False
        if (
                packet.source_id not in self.flock_lsp or
                self.flock_lsp[packet.source_id][1] < packet.created_at
            ):
            self.flock_lsp[packet.source_id] = (packet.data["value"], packet.created_at)
            self.update_leader()
            return True
        return False

    def handle(self, packet, packet_meta):
        if packet.data is None: return
        if packet.data["type"] == "lsp_update":
            self.handle_longest_shortest_path_update(packet, packet_meta)
        elif packet.data["type"] == "edges_removed":
            self.handle_removed_edges_update(packet, packet_meta)

    def handle_added_edges(self, added_edges):
        if not len(added_edges): return
        # for n_id in added_edges:
        #     # If a path exists that 
        #     if 

    def handle_removed_edges(self, removed_edges):
        if not len(removed_edges): return
        
        # Find any routes that relied on this link
        cut_routes = [(n_id,timestamp + 1) for n_id,(neighbor,path_length,timestamp) in self.route_t.items() if neighbor in removed_edges]

        if len(list(cut_routes)) == 0: return
        
        # Update routing table
        for n_id,_ in cut_routes:
            self.route_t[n_id] = (None, 0, self.route_t[n_id][2])
            if n_id in self.flock_lsp:
                del self.flock_lsp[n_id]
        
        # Send to others
        # print("SENDING edges removed", cut_routes)
        data = {
            "type": "edges_removed",
            "value": cut_routes
        }
        p = Packet(data, self.id, None)
        self.broadcast(p)
        # print("sending edge removal")
        # Now have both rebroadcast to learn shortest path
        self.local_timestamp += 1
        self.broadcast(Packet(None, self.id, None))
        self.update_leader()

    def handle_removed_edges_update(self, packet, packet_meta):
        assert(packet.data["type"] == "edges_removed")
        if (packet.source_id == self.id): return False
        value = packet.data["value"]
        # If used the relay node as beginning of route to removed node, then relay
        # print("handling edge update", value)
        res = [(n_id,timestamp) for n_id,timestamp in value if n_id in self.route_t and self.route_t[n_id][0] == packet_meta.from_id]
        # print("filtering ", len(res), len(packet.data["value"]))
        assert(packet_meta.from_id is not None)
        if not len(res):
            return False
        # print("filtering 2", len(res), len(packet.data["value"]))
        packet.data["value"] = res
        for n_id,timestamp in packet.data["value"]:
            self.route_t[n_id] = (None, 0, self.route_t[n_id][2])
            if n_id in self.flock_lsp and self.flock_lsp[n_id][1] < packet.created_at:
                del self.flock_lsp[n_id]
        # print("relaying edge removal", packet.data["value"])
        self.broadcast(packet, packet_meta)
        self.local_timestamp += 1
        self.broadcast(Packet(None, self.id, None))
        self.share_longest_shortest_path()
        # self.update_leader()
        return True


    def handle_updated_edges(self, updated_edges):
        if not len(updated_edges): return

    def detect(self):
        self.refresh_neighbors()

        # detect if changes 
        added,removed,updated = self.compare_neighbors()
        if len(added): self.handle_added_edges(added)
        if len(removed): self.handle_removed_edges(removed)
        if len(updated): self.handle_updated_edges(updated)

        self.refresh_neighbors_history()





import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
import argparse
from collections import OrderedDict 
from structures.system import Graph, Node
from helpers.fiedler import fiedler, normalized_fiedler
from data.formations import formations
from helpers.get_edges import get_edges
from helpers.print_graph import print_graph
from algorithms.floyd_warshall import floydWarshall, floydWarshallCenter
from algorithms.prims import Graph as PrimGraph
from algorithms.specify import SpecifySmallStep
from algorithms.centerrank import centerrank
import random
from structures.communication_network import NeighborCommunication, BroadcastNode
from structures.timed_communication_network import TimedNeighborCommunication, TimedBroadcastNode, TimedEnvironment, DynamicTimedEnvironment
from structures.id_manager import IdManager
import pandas as pd
import networkx as nx
from helpers.mkdir_p import mkdir_p
import matplotlib.ticker as plticker
from algorithms.connected_components import subGraphs

random.seed(12)
INF  = 99999


def tie_breaker(leaders):
    if len(leaders) == 0: return -1
    # print("leaders", leaders)
    return max(leaders)

def recalibrate(env, manager, nodes):
    states = []
    t_steps = env.time
    last_t_steps = t_steps
    env.detect()
    while(len(env.packet_queue)):
        # print("in process", sum(len(node.in_queue) for node in nodes))
        # t_steps += 1
        last_t_steps = t_steps
        env.run()
        t_steps = env.time
        if last_t_steps != t_steps: 
            states.append((t_steps,[tie_breaker(node.leader) for node in nodes]))
    states.append((t_steps,[tie_breaker(node.leader) for node in nodes]))
    # print("routes",list(node.route_t for node in nodes))
    print("lsp", list(nodes[3].flock_lsp))
    
    # Assert all equal
    center = [set(manager.get_index(leader) for leader in node.leader) for node in nodes]
    # for i,node in enumerate(nodes):
    #     if i != 0:
    #         leader_set = set(manager.get_index(leader) for leader in node.leader)
    #         assert(len(center.symmetric_difference(leader_set)) == 0)

    return t_steps, states, center



def plot_states(node_states, correct, save_name = None):
    # print("correct", correct)
    # print("node_states", node_states)

    steps = [t for (t,_) in node_states]
    lines = [[] for _ in node_states[0][1]]
    for i, (t, states) in enumerate(node_states):
        for j,bot_val in enumerate(states):
            lines[j].append(bot_val)

    _, ax = plt.subplots()
    loc = plticker.MultipleLocator(base=(5.0 if len(steps) < 40 else 10.0)) # this locator puts ticks at regular intervals
    ax.xaxis.set_major_locator(loc)
    # Plot correct answer as black dotted line
    num_cc = max([len(y) for _,y in correct])
    for i in range(len(correct)):
        delta = num_cc - len(correct[i][1])
        if delta > 0:
            for j in range(delta):
                correct[i][1].append(correct[i][1][0])

    true_lines = [[] for _ in range(num_cc)]
    for i, (t, states) in enumerate(correct):
        for j,bot_val in enumerate(states):
            true_lines[j].append(bot_val)
    # print("steps",steps)
    # print("true_lines",true_lines)
    # print("lines",lines)
    for data in lines:
        line, = ax.plot(steps, data)
    for data in true_lines:
        line, = ax.plot(steps, data, '-', color = 'black', linewidth=4, marker="*", linestyle = 'None')
    
    plt.legend()
    mkdir_p("figures/leader_election_dynamics")
    if save_name: 
        plt.savefig("figures/leader_election_dynamics/{}.png".format(save_name))
        plt.close()
    else: plt.show()


if __name__ == "__main__":
    
    # 
    # Arguments
    # 
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--formation", type=int, help="enter a formation number/id",
                        nargs='?', default=0, const=0, choices=range(0, len(formations) + 1))
    args = parser.parse_args()

    # To Create a Formation, add one to `formations.py`
    if args.formation == 0:
        forms = formations
    else: 
        form = formations[args.formation - 1]
        forms = [form]

    # 
    # Run Simulations
    # 

    dash = '-' * 100
    columns = ["Formation", "Time", "Test Result", "Predicted", "Center", "R", "D"]
    print(dash)
    print('{:<24s}{:<6s}{:<12s}{:<42s}{:<42s}{:<12s}{:<12s}'.format(*columns))
    print(dash)

    # Preload classes to allow decision tree to make only once

    def format_edge(graph,u,v):
        if u == v: return 0
        if graph[u][v]: return graph[u][v]
        else: return INF
    def format_graph(graph):
        V = len(graph)
        return [[format_edge(graph,i,j) for j in range(V)] for i in range(V)]

    def perform_test(formation, name, generate_figure = False):
        graph = formation["full"]
        # Setup flock
        flock_size = len(graph)
        nodes = [TimedBroadcastNode(flock_size) for i in range(flock_size)]
        manager = IdManager(graph, nodes)
        env = DynamicTimedEnvironment(graph, manager)
        for node in nodes:
            node.set_communicator(TimedNeighborCommunication(node.id, manager, env))

        # Fill routing table
        for node in nodes:
            node.setup()
        true_states = [(0,[tie_breaker(floydWarshallCenter(format_graph(graph))[0])])]
        states = [(0,[tie_breaker(node.leader) for node in nodes])]

        for t, f_t in enumerate(formation["timeline"]):
            f_t(env)

            # FW
            true_centers, radiuses, diameters = [],[],[]
            true_centers_full = []
            sub_graphs = subGraphs(env.adj_matrix)
            # print("sub graphs", sub_graphs)
            for (graph_map,sub_graph) in sub_graphs:
                formatted = format_graph(sub_graph)
                center, radius, diameter = floydWarshallCenter(formatted)
                true_centers.append(tie_breaker(list(graph_map[n] for n in center)))
                true_centers_full.append(set(graph_map[n] for n in center))
                radiuses.append(radius)
                diameters.append(diameter)

            # Leader election
            t_steps,new_states, predicted = recalibrate(env, manager, nodes)
            predicted_res = [predicted[graph_map[0]] for (graph_map,_) in sub_graphs]
            for state_t,state_list in new_states:
                true_states.append((state_t, true_centers))
            states += new_states
            print("took t={} to recalibrate".format(t_steps))

            result = ""
            # If not predicted any false and at least one element in predicted also in true
            # if (len(set(predicted).symmetric_difference(center)) == 0): result = "SUCCESS"

            print('{:<24s}{:<6s}{:<12s}{:<42s}{:<42s}{:<12s}{:<12s}'.format(name, "t={}".format(t), result, str(predicted), str(list(true_centers_full)), str(list(radiuses)), str(list(diameters))))
            print()
        
        print("took t={} to complete timeline and election".format(t_steps))
        # print("processed ", [(node.id, node.packets_processed) for node in nodes])
        # print("sent ", [(node.id, node.packets_sent) for node in nodes])
        # print("total processed ", sum([node.packets_processed for node in nodes]))
        # print("total sent ", sum([node.packets_sent for node in nodes]))
        # print("routes", longest_route)
        # print("routes for 0", nodes[0].route_t)

        predicted, states = list(center), states



        if generate_figure: plot_states(states, true_states, save_name=name)

    alg_results = OrderedDict()
    for formation in forms:
        perform_test(formation, formation["name"], True)

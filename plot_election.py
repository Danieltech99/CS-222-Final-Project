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
from algorithms.specify import SpecifySmallStep
import random
from structures.communication_network import NeighborCommunication, BroadcastNode
from structures.timed_communication_network import TimedNeighborCommunication, TimedBroadcastNode, TimedEnvironment
from structures.id_manager import IdManager
import pandas as pd
import networkx as nx
from helpers.mkdir_p import mkdir_p
import matplotlib.ticker as plticker

random.seed(12)
INF  = 99999


def tie_breaker(leaders):
    if len(leaders) == 0: return -1
    return min(leaders)
def evaluate_noisy_broadcast(graph):
    # Setup flock
    flock_size = len(graph)
    nodes = [TimedBroadcastNode(flock_size) for i in range(flock_size)]
    manager = IdManager(graph, nodes)
    env = TimedEnvironment(graph, manager)
    for node in nodes:
        node.set_communicator(TimedNeighborCommunication(node.id, manager, env))

    # Fill routing table
    for node in nodes:
        node.setup()
    states = [(0,[tie_breaker(node.leader) for node in nodes])]
    t_steps = 0
    last_t_steps = t_steps
    while(len(env.packet_queue)):
        # print("in process", sum(len(node.in_queue) for node in nodes))
        # t_steps += 1
        last_t_steps = t_steps
        env.run()
        t_steps = env.time
        if last_t_steps != t_steps: 
            states.append((t_steps,[tie_breaker(node.leader) for node in nodes]))
    states.append((t_steps,[tie_breaker(node.leader) for node in nodes]))
    
    print("took t={} to complete broadcast and election".format(t_steps))

    # Assert all equal
    center = set(manager.get_index(leader) for leader in nodes[0].leader)
    # print("processed ", [(node.id, node.packets_processed) for node in nodes])
    # print("sent ", [(node.id, node.packets_sent) for node in nodes])
    # print("total processed ", sum([node.packets_processed for node in nodes]))
    # print("total sent ", sum([node.packets_sent for node in nodes]))
    # print("routes", longest_route)
    # print("routes for 0", nodes[0].route_t)

    return list(center), states



def plot_states(node_states, correct, save_name = None):

    steps = [t for (t,_) in node_states]
    lines = [[] for _ in node_states[0][1]]
    for i, (t, states) in enumerate(node_states):
        for j,bot_val in enumerate(states):
            lines[j].append(bot_val)

    _, ax = plt.subplots()
    loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
    ax.xaxis.set_major_locator(loc)
    # Plot correct answer as black dotted line
    for data in lines:
        line, = ax.plot(steps, data)
    ax.plot(steps, [correct] * len(steps), '-', color = 'black', linewidth=4, marker="*", linestyle = 'None')
    
    plt.legend()
    mkdir_p("figures/leader_election_convergence")
    if save_name: 
        plt.savefig("figures/leader_election_convergence/{}.png".format(save_name))
        plt.close()
    else: plt.show()


if __name__ == "__main__":
    
    forms = formations

    # 
    # Run Simulations
    # 

    dash = '-' * 100
    columns = ["Formation", "Test Result", "Predicted", "Center", "R", "D"]
    print(dash)
    print('{:<24s}{:<16s}{:<24s}{:<24s}{:<4s}{:<4s}'.format(*columns))
    print(dash)

    # Preload classes to allow decision tree to make only once

    def format_edge(graph,u,v):
        if u == v: return 0
        if graph[u][v]: return graph[u][v]
        else: return INF
    def format_graph(graph):
        V = len(graph)
        return [[format_edge(graph,i,j) for j in range(V)] for i in range(V)]

    def perform_test(graph, name, generate_figure = False):
        formatted = format_graph(graph)
        # print("formatted")
        # print_graph(formatted)
        center, radius, diameter = floydWarshallCenter(formatted)
        predicted, states = evaluate_noisy_broadcast(graph)
        result = ""
        # If not predicted any false and at least one element in predicted also in true
        if (len(set(predicted).symmetric_difference(center)) == 0): result = "SUCCESS"

        print('{:<24s}{:<16s}{:<24s}{:<24s}{:<4d}{:<4d}'.format(name, result, str(predicted), str(center), radius, diameter))
        print()

        if generate_figure: plot_states(states, tie_breaker(center), save_name=name)

    alg_results = OrderedDict()
    for formation in forms:
        for key in ["full", "tree"]:
            perform_test(formation[key], formation["name"] + " " + key, True)

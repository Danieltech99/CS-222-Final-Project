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
from structures.communication_network import DirectCommunication, BroadcastNode, IdManager
import pandas as pd
import networkx as nx

random.seed(12)
INF  = 99999


def random_graph(size, target_fiedler = 0.5):
    graph = np.array([np.array([0 if i == j else 1 for j in range(size)]) for i in range(size)])
    tree = SpecifySmallStep(graph).create_graph(target_fiedler, bound="one")
    return tree

def random_weighted_graph(size, target_fiedler = 0.5):
    # graph = np.array([np.array([0 if i == j else random.randint(1,40) for j in range(size)]) for i in range(size)])
    graph = np.array([np.array([0 if i == j else random.randint(1,40) for j in range(size)]) for i in range(size)])
    # Make undirected (Currently only supports undirected)
    for u in range(len(graph)):
        for v in range(len(graph)):
            if u < v:
                graph[v][u] = graph[u][v]
    tree = SpecifySmallStep(graph).create_graph(target_fiedler, bound="one")
    return tree

def generate_random_graphs(n, target_fiedler = 0.5, random_w = False):
    # Generate fully connected
    graphs = []
    for i in range(n):
        size = (i + 1) * 5
        tree = random_weighted_graph(size,target_fiedler) if random_w else random_graph(size, target_fiedler)
        # print(tree)
        graphs.append(tree)
    return graphs


def evaluate_broadcast(graph):
    # Setup flock
    nodes = [BroadcastNode() for i in range(len(graph))]
    manager = IdManager(graph, nodes)
    for node in nodes:
        node.set_communicator(DirectCommunication(graph, node.id, manager))

    # Fill routing table
    for node in nodes:
        node.broadcast()
    t_steps = 0
    while(sum(len(node.in_queue) for node in nodes)):
        # print("in process", sum(len(node.in_queue) for node in nodes))
        t_steps += 1
        for node in nodes: node.process()
    
    print("took t={} to complete broadcast".format(t_steps))

    longest_route = [max(((manager.get_index(node.id), path[1]) for path in node.route_t.values()), key=lambda t: t[1]) for node in nodes]
    # print("processed ", [(node.id, node.packets_processed) for node in nodes])
    # print("sent ", [(node.id, node.packets_sent) for node in nodes])
    # print("total processed ", sum([node.packets_processed for node in nodes]))
    # print("total sent ", sum([node.packets_sent for node in nodes]))
    # print("routes", longest_route)
    # print("routes for 0", nodes[0].route_t)
    center_min = min(longest_route, key=lambda o: o[1])[1]
    center = [o[0] for o in longest_route if o[1] == center_min]

    return center


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

    def perform_test(graph, name):
        formatted = format_graph(graph)
        # print("formatted")
        # print_graph(formatted)
        center, radius, diameter = floydWarshallCenter(formatted)
        predicted = evaluate_broadcast(graph)
        result = ""
        # If not predicted any false and at least one element in predicted also in true
        if (len(set(predicted) - set(center)) == 0 and len(set(center).intersection(predicted)) > 0): result = "SUCCESS"

        print('{:<24s}{:<16s}{:<24s}{:<24s}{:<4d}{:<4d}'.format(name, result, str(predicted), str(center), radius, diameter))
        print()

    alg_results = OrderedDict()
    for formation in forms:
        for key in ["full", "tree"]:
            perform_test(formation[key], formation["name"] + " " + key)
    
    print()

    graphs = generate_random_graphs(5, 0.75)
    for graph_i, graph in enumerate(graphs):
        perform_test(graph, "Random Size {}".format(len(graph)))
        
    print()
        
    graphs = generate_random_graphs(5)
    for graph_i, graph in enumerate(graphs):
        perform_test(graph, "Random Size {}".format(len(graph)))
        
    print()

    graphs = generate_random_graphs(5, 0.25)
    for graph_i, graph in enumerate(graphs):
        perform_test(graph, "Random Size {}".format(len(graph)))
        
    print()

    print("RANDOM GRAPHS:")

    print()

    graphs = generate_random_graphs(2, 0.75, True)
    for graph_i, graph in enumerate(graphs):
        perform_test(graph, "Random Size {}".format(len(graph)))
        
    print()
        
    graphs = generate_random_graphs(2, 0.5, True)
    for graph_i, graph in enumerate(graphs):
        perform_test(graph, "Random Size {}".format(len(graph)))
        
    print()

    graphs = generate_random_graphs(2, 0.25, True)
    for graph_i, graph in enumerate(graphs):
        perform_test(graph, "Random Size {}".format(len(graph)))
        
    print()
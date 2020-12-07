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

INF  = 99999

def generate_random_graphs(n):
    # Generate fully connected
    graphs = []
    for i in range(n):
        size = (i + 1) * 5
        graph = np.array([np.array([0 if i == j else 1 for j in range(size)]) for i in range(size)])
        tree = SpecifySmallStep(graph).create_graph(0.5, bound="one")
        # print(tree)
        graphs.append(tree)
    return graphs

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

    dash = '-' * 40
    columns = ["Formation", "Predicted Center", "Predicted Min", "Predicted Max", "Center", "Radius", "Diameter"]
    print(dash)
    print('{:<24s}{:<16s}{:<16s}{:<16s}{:<16s}{:<16s}{:<16s}'.format(*columns))
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

        ranks = centerrank(graph)
        eranks = [(i,v) for i,v in enumerate(ranks)]
        print("eranks", eranks)
        print('{:<24s}{:<16d}{:<16d}{:<16d}{:<16d}{:<16d}{:<16d}'.format(name, 0, min(eranks, key=lambda o: o[1])[0], max(eranks, key=lambda o: o[1])[0], center, radius, diameter))

    alg_results = OrderedDict()
    for formation in forms:
        for key in ["full", "tree"]:
            perform_test(formation[key], formation["name"] + " " + key)
    
    print()
        
    graphs = generate_random_graphs(5)
    for graph in graphs:
        perform_test(graph, "Random Size {}".format(len(graph)))
    print()
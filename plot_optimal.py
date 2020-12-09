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
from algorithms.floyd_warshall import floydWarshall, floydWarshallCenter, pathSum
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

def bar_graph(data, save_name):

    x = range(len(data))
    energy = data

    x_pos = [i for i, _ in enumerate(x)]

    plt.bar(x_pos, energy)
    plt.xlabel("Leader")
    plt.ylabel("Hops From Leader to All Followers")
    plt.title("Network Hops For Selected Leader")

    plt.xticks(x_pos, x)

    mkdir_p("figures/compare_leader")
    plt.savefig("figures/compare_leader/{}.png".format(save_name))
    plt.close()

INF  = 99999
def format_edge(graph,u,v):
    if u == v: return 0
    if graph[u][v]: return graph[u][v]
    else: return INF
def format_graph(graph):
    V = len(graph)
    return [[format_edge(graph,i,j) for j in range(V)] for i in range(V)]

if __name__ == "__main__":
    for formation in formations:
        for key in ["full", "tree"]:
            path_sum = pathSum(format_graph(formation[key]))
            bar_graph(path_sum, save_name=formation["name"] + " " + key)
            

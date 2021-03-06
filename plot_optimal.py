import numpy as np
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
import argparse
from collections import OrderedDict 
from helpers.fiedler import fiedler, normalized_fiedler
from data.formations import formations
from helpers.get_edges import get_edges
from helpers.print_graph import print_graph
from algorithms.floyd_warshall import floydWarshall, floydWarshallCenter, pathSum
from algorithms.specify import SpecifySmallStep
import random
from structures.timed_communication_network import TimedNeighborCommunication, TimedBroadcastNode, TimedEnvironment, DynamicTimedEnvironment
from structures.id_manager import IdManager
import pandas as pd
import networkx as nx
from helpers.mkdir_p import mkdir_p
import matplotlib.ticker as plticker
from algorithms.connected_components import subGraphs

def bar_graph(data, data2, centers, save_name):
    fig, axs = plt.subplots((2),figsize=(6,10))

    x = range(len(data))
    x_pos = [i for i, _ in enumerate(x)]
    colors = ["b" if i in centers else 'grey' for i, _ in enumerate(x)]

    axs[0].bar(x_pos, data, color=colors)
    axs[0].xaxis.set_label_text("Leader")
    axs[0].yaxis.set_label_text("Hops From Leader to Furthest Follower")
    # axs[0].title("Route Max Length For Selected Leader")
    # axs[0].xticks(x_pos, x)
    
    axs[1].bar(x_pos, data2, color=colors)
    axs[1].xaxis.set_label_text("Leader")
    axs[1].yaxis.set_label_text("Hops From Leader to All Followers")
    # axs[1].title("Network Hops For Selected Leader")
    # axs[1].xticks(x_pos, x)

    fig.suptitle(save_name, size="xx-large")

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
        # Only test connected graphs
        for key in ["full", "tree"]:
            if fiedler(formation[key]) < 0.05:
                continue
            path_sum, maximum, center = pathSum(format_graph(formation[key]))
            print(formation["name"] + " " + key, "max", maximum, "sum", path_sum)
            bar_graph(maximum, path_sum, center, save_name=formation["name"] + " " + key)
            

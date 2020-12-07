import sys

def print_graph(graph):
    for row in graph:
        print(" ".join(["INF" if i == str(sys.maxsize) else i for i in map(str,row)]))
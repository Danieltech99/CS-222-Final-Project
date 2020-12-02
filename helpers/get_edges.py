def get_edges(graph):
    l = len(graph)
    return sorted([(u,v) for u in range(l) for v in range(u + 1, l) if graph[u][v]])
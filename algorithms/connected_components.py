def DFSUtil(graph, temp, v, visited):

    # Mark the current vertex as visited
    visited[v] = True

    # Store the vertex to list
    temp.append(v)

    # Repeat for all vertices adjacent
    # to this vertex v
    for i,w in enumerate(graph[v]):
        if w > 0:
            if visited[i] == False:

                # Update the list
                temp = DFSUtil(graph, temp, i, visited)
    return temp

# Method to retrieve connected components
# in an undirected graph
def connectedComponents(graph):
    visited = []
    cc = []
    for i in range(len(graph)):
        visited.append(False)
    for v in range(len(graph)):
        if visited[v] == False:
            temp = []
            cc.append(DFSUtil(graph, temp, v, visited))
    return cc

def subGraphs(graph):
    comps = connectedComponents(graph)
    sub_graphs = []
    for c in comps:
        component = sorted(c)
        map = {i:n for i,n in enumerate(component)}
        sub_g = []
        for u in range(len(component)):
            row = []
            for v in range(len(component)):
                row.append(None)
            sub_g.append(row)
        for u_new,u in enumerate(component):
            for v_new,v in enumerate(component):
                sub_g[u_new][v_new] = graph[u][v]
        sub_graphs.append((map,sub_g))
    return sub_graphs

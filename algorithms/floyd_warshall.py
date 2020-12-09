import sys

# Python Program for Floyd Warshall Algorithm 
# Originally Sourced from GeeksforGeeks
  
  
# Define infinity as the large enough value. This value will be 
# used for vertices not connected to each other 
# Cant use max bc of addition overflow
INF  = 99999
  
# Solves all pair shortest path via Floyd Warshall Algorithm 
def floydWarshall(graph, print_log = False): 
    V = len(graph)
  
    """ dist[][] will be the output matrix that will finally 
        have the shortest distances between every pair of vertices """
    """ initializing the solution matrix same as input graph matrix 
    OR we can say that the initial values of shortest distances 
    are based on shortest paths considering no  
    intermediate vertices """
    dist = list(map(lambda i : list(map(lambda j : j , i)) , graph))
      
    """ Add all vertices one by one to the set of intermediate 
     vertices. 
     ---> Before start of an iteration, we have shortest distances 
     between all pairs of vertices such that the shortest 
     distances consider only the vertices in the set  
    {0, 1, 2, .. k-1} as intermediate vertices. 
      ----> After the end of a iteration, vertex no. k is 
     added to the set of intermediate vertices and the  
    set becomes {0, 1, 2, .. k} 
    """
    for k in range(V): 
  
        # pick all vertices as source one by one 
        for i in range(V): 
  
            # Pick all vertices as destination for the 
            # above picked source 
            for j in range(V): 
  
                # If vertex k is on the shortest path from  
                # i to j, then update the value of dist[i][j] 
                dist[i][j] = min(dist[i][j], dist[i][k]+ dist[k][j]) 
    if print_log: printSolution(dist) 
    return dist
  

# A utility function to print the solution 
def printSolution(dist): 
    V = len(dist)
    print("Following matrix shows the shortest distances between every pair of vertices")
    for i in range(V): 
        for j in range(V): 
            if(dist[i][j] == INF): 
                print("{:>7s}\t".format("INF"), end="")
            else: 
                print("{:>7d}\t".format(dist[i][j]), end="")
            if j == V-1: 
                print("")
  
def floydWarshallCenter(graph, print_stats = False):
    dist = floydWarshall(graph, print_stats)
    N = len(dist)
    longest_shortest_path = [max([(dist,i) for j, dist in enumerate(dist[i])], key=lambda o: o[0]) for i in range(N)]
    if print_stats: print("FW longest shwrtest", longest_shortest_path)
    center_min = min(longest_shortest_path, key=lambda o: o[0])[0]
    center = [o[1] for o in longest_shortest_path if o[0] == center_min]
    diameter = max(longest_shortest_path, key=lambda o: o[0])
    if print_stats: 
        print("Found center node: {} with distance: {}, diameter: {}, radius: {}".format(center[1], center[0], diameter[0],  center[0]))
    return center, center_min, diameter[0]

def pathSum(graph):
    dist = floydWarshall(graph)
    N = len(dist)
    res = [sum([dist for j, dist in enumerate(dist[i])]) for i in range(N)]
    print("sum", res, dist)
    return res
  
if __name__ == "__main__":
    # GeeksforGeeks Test for Floyd Warshall
    # Driver program to test the above program 
    # Let us create the following weighted graph 
    """ 
                10 
        (0)------->(3) 
            |         /|\ 
        5 |          | 
            |          | 1 
        \|/         | 
        (1)------->(2) 
                3           """
    graph = [
                [   0,       5,    INF,   10], 
                [   5,       0,      3,  INF],   
                [ INF,       3,      0,    1],  
                [   10,    INF,      1,    0] 
            ] 
    # Expected Output
    # Following matrix shows the shortest distances between every pair of vertices
    #       0      5      8      9
    #     INF      0      3      4
    #     INF    INF      0      1
    #     INF    INF    INF      0
    floydWarshallCenter(graph, True)
    print()

    # GeeksforGeeks Tests for Center, etc
    # https://www.geeksforgeeks.org/graph-measurements-length-distance-diameter-eccentricity-radius-center/

    # Center A
    # https://media.geeksforgeeks.org/wp-content/uploads/g3.jpg.jpg
    floydWarshallCenter([ 
        [0, 1, 1, 1, 1],
        [1, 0, INF, INF, INF],
        [1, INF, 0, INF, INF],
        [1, INF, INF, 0, INF],
        [1, INF, INF, INF, 0],
    ], True)
    print()
    # Radius 2
    # Diameter 3
    # https://media.geeksforgeeks.org/wp-content/uploads/g2-7.png
    floydWarshallCenter([
        [0, INF, 1, INF, INF, INF, INF],
        [INF, 0, 1, INF, INF, INF, INF],
        [1, 1, 0, 1, 1, 1, INF],
        [INF, INF, 1, 0, INF, INF, INF],
        [INF, INF, 1, INF, 0, INF, INF],
        [INF, INF, 1, INF, INF, 0, 1],
        [INF, INF, INF, INF, INF, 1, 0],
    ], True)
    print()
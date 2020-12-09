import numpy as np
from structures.system import Node

# To Create a Formation
# ... add an object with `name`, `nodes`, `full`, `tree`

# Timeline
# Step 1: Original
# Step 2: Add Node
# Step 3: Add Edges
# Step 4: Remove Edges
# Step 5: Remove Node



formations = [
    # circular formation
    {
        "name": "Circular",
        "nodes": [Node(4.0), Node(2.0), Node(-1.0), Node(3.0), Node(0.0), Node(-3.0)],
        "full": np.array([
                        [0, 1, 1, 1, 1, 1],
                        [1, 0, 1, 1, 1, 1],
                        [1, 1, 0, 1, 1, 1],
                        [1, 1, 1, 0, 1, 1],
                        [1, 1, 1, 1, 0, 1],
                        [1, 1, 1, 1, 1, 0]]),
        "tree": np.array([
                        [0, 1, 0, 0, 0, 0],
                        [1, 0, 1, 0, 0, 0],
                        [0, 1, 0, 1, 0, 0],
                        [0, 0, 1, 0, 1, 0],
                        [0, 0, 0, 1, 0, 1],
                        [0, 0, 0, 0, 1, 0]]),
        "timeline": [
            lambda env: env,
            lambda env: env.remove_edge(1,3).remove_edge(1,4).remove_edge(1,5),
            lambda env: env.remove_all_edges(2), # Indices change after remove
            lambda env: env.add_edge(1,3).add_edge(1,4).add_edge(1,5),
            lambda env: env.add_all_edges(2)
        ]
    },

    # wedge formation
    {
        "name": "Wedge",
        "nodes": [Node(4.0), Node(2.0), Node(-1.0), Node(3.0), Node(0.0), Node(1.0), Node(-2.0)],
        "full": np.array([
                        [0, 1, 0, 1, 0, 0, 0],
                        [1, 0, 1, 1, 0, 0, 0],
                        [0, 1, 0, 1, 0, 0, 0],
                        [1, 1, 1, 0, 1, 1, 1],
                        [0, 0, 0, 1, 0, 1, 0],
                        [0, 0, 0, 1, 1, 0, 1],
                        [0, 0, 0, 1, 0, 1, 0]]),
        "tree": np.array([
                        [0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0],
                        [1, 1, 1, 0, 1, 1, 1],
                        [0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0]]),
        "timeline": [
            lambda env: env,
            lambda env: env.remove_edges([(1,0),(1,2)]),
            lambda env: env.remove_all_edges(5), # Indices change after remove
            lambda env: env.add_edges([(1,0),(1,2)]),
            lambda env: env.add_edges([(5,3),(5,4),(5,6)])
        ]
    },

    # linear formation
    {
        "name": "Line",
        "nodes": [Node(4.0), Node(2.0), Node(-1.0), Node(3.0), Node(0.0)],
        "full": np.array([
                        [0, 1, 1, 1, 1],
                        [1, 0, 1, 1, 1],
                        [1, 1, 0, 1, 1],
                        [1, 1, 1, 0, 1],
                        [1, 1, 1, 1, 0]]),
        "tree": np.array([
                        [0, 1, 0, 0, 0],
                        [1, 0, 1, 0, 0],
                        [0, 1, 0, 1, 0],
                        [0, 0, 1, 0, 1],
                        [0, 0, 0, 1, 0]]),
        "timeline": [
            lambda env: env,
            lambda env: env.remove_edges([(0,2),(0,3),(0,4)]),
            lambda env: env.remove_all_edges(3), # Indices change after remove
            lambda env: env.add_edges([(0,2),(0,4)]), 
            lambda env: env.add_all_edges(3)
        ]
    },

    {
        "name": "Split-Merge",
        "nodes": [Node(4.0), Node(2.0), Node(-1.0), Node(3.0), Node(0.0)],
        "full": np.array([
                        [0, 1, 0, 1, 0, 0, 0],
                        [1, 0, 1, 1, 0, 0, 0],
                        [0, 1, 0, 1, 0, 0, 0],
                        [1, 1, 1, 0, 1, 1, 1],
                        [0, 0, 0, 1, 0, 1, 0],
                        [0, 0, 0, 1, 1, 0, 1],
                        [0, 0, 0, 1, 0, 1, 0]]),
        "tree": np.array([
                        [0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0],
                        [1, 1, 1, 0, 1, 1, 1],
                        [0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0],
                        [0, 0, 0, 1, 0, 0, 0]]),
        "timeline": [
            lambda env: env,
            lambda env: env.remove_edges([(0,3),(1,3),(2,3),(5,3),(6,3)]),
            lambda env: env,
            lambda env: env.add_edges([(2,3)]), 
            lambda env: env,
        ]
    },

    {
        "name": "Rebalance-Flocks",
        "nodes": [Node(4.0), Node(2.0), Node(-1.0), Node(3.0), Node(0.0), Node(-3.0)],
        "full": np.array([
                        [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        ]),
        "tree": np.array([
                        [0, 1, 0, 0, 0, 0],
                        [1, 0, 1, 0, 0, 0],
                        [0, 1, 0, 1, 0, 0],
                        [0, 0, 1, 0, 1, 0],
                        [0, 0, 0, 1, 0, 1],
                        [0, 0, 0, 0, 1, 0]]),
        "timeline": [
            lambda env: env.add_edge(2,6).add_edge(3,11,20),
            lambda env: env,
            lambda env: env.remove_edge(2,6),
            lambda env: env,
            lambda env: env.add_edge(12,2).add_edge(12,6),
            lambda env: env,
        ]
    },

    {
        "name": "Recalibrate-Flocks",
        "nodes": [Node(4.0), Node(2.0), Node(-1.0), Node(3.0), Node(0.0), Node(-3.0)],
        "full": np.array([
                        [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                        [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0],
                        [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
                        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        ]),
        "tree": np.array([
                        [0, 1, 0, 0, 0, 0],
                        [1, 0, 1, 0, 0, 0],
                        [0, 1, 0, 1, 0, 0],
                        [0, 0, 1, 0, 1, 0],
                        [0, 0, 0, 1, 0, 1],
                        [0, 0, 0, 0, 1, 0]]),
        "timeline": [
            lambda env: env.add_edge(12,2,5).add_edge(12,6,5).add_edge(3,11,20),
            lambda env: env,
            lambda env: env.remove_edge(3,11).add_edge(3,11,5),
            lambda env: env,
        ]
    },
        
]
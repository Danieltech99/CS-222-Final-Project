import numpy as np
from structures.system import Node

# To Create a Formation
# ... add an object with `name`, `nodes`, `full`, `tree`

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
                        [0, 0, 0, 0, 1, 0]])
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
                        [0, 0, 0, 1, 0, 0, 0]])
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
                        [0, 0, 0, 1, 0]])
    }
        
]
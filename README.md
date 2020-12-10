# CS-222-Final-Project


*Abstract: We present an algorithm to elect a leader such as to optimize information distribution from leader to followers in mobile multi-agent robotic systems; the proposed algorithm is simple and only requires agents to communicate with their neighbors yet resilient to topology changes (thus applicable to mobile ad hoc networks). The algorithms ensure that eventually each agent in each connected component will locally determine the set of most optimal leaders.*

Paper: [Decentralized Optimal Leader Election for Shortest-Path Routing in Mobile Ad Hoc Networks](paper/CS_222_Final_Project.pdf)

# Formations

Formations:
- 0: All
- 1: Circular
- 2: Wedge
- 3: Line
- 4: Split-Merge
- 5: Rebalance-Removal
- 6: Rebalance-Update



## Plot Leader Selection

This file generates bar charts measuring hops to furthest follower (top) and total hops to all followers (bottom) for each selected leader. Graph centers (calculated by the Floyd Warshall Algorithm) are colored as blue bars. Outputs a figure for each formation to the `figures/compare_leader/` directory.

```
python3 plot_optimal.py
```

### Configuring:

**Formations:** to change the formations being tested, add a formation to `data/formations.py`, making sure to follow the existing format. **This program only supports connected graphs.**



## Plot Static Election

This file generates plots that show convergence in the network over time. In this chart, each line is a agent; the x-axis is time; the y-axis is id of the selected leader; the stars represent the optimal leader. Because there can be multiple optimal leaders we chose the agent with the maximum id as the (default) tie breaker. Outputs a figure for each formation to the `figures/leader_election_convergence/` directory.

```
python3 plot_election.py --formation [0-3]
```
The optional formation flag allows you to specify which formation to run. The default (0) runs all formations.

### Configuring:

**Formations:** to change the formations being tested, add a formation to `data/formations.py`, making sure to follow the existing format. **This program only supports connected graphs.**

**Tie Breaker:** to change how a tie is broken, edit `tie_breaker`. This function takes in a list of optimal leaders and returns a single identifier/element.



## Plot Dynamic Election

This file generates plots that show convergence in the network over time. In this chart, each line is a agent; the x-axis is time; the y-axis is id of the selected leader; the stars represent the optimal leader; when there are multiple connected components, there are multiple horizontal lines of stars to represent the (max) optimal leader for each connected component. Because there can be multiple optimal leaders we chose the agent with the maximum id as the (default) tie breaker. Outputs a figure for each formation to the `figures/leader_election_convergence/` directory.

```
python3 plot_dynamic_election.py --formation [0-6]
```
The optional formation flag allows you to specify which formation to run. The default (0) runs all formations.

### Configuring:

**Formations:** to change the formations being tested, add a formation to `data/formations.py`, making sure to follow the existing format.

This program also introduces timelines. These are an array of operations that represent the changes of the topology at each time step. Each timeline is a property of a formation in `data/formations.py`. The supported topology operations are provided by `DynamicTimedEnvironment` in `structures/timed_communication_network.py`. Note: to update an edge's weight, remove the edge and add it again, or just add it; the add method takes a third parameter which is the edge weight.

**Tie Breaker:** to change how a tie is broken, edit `tie_breaker`. This function takes in a list of optimal leaders and returns a single identifier/element.



## Additional Tests for Static Graphs

This program tests the algorithm with each of the formations as well with a number of generated graphs (using the Specify algorithm from https://github.com/Danieltech99/CS-286-Final-Project) and a number of graphs with random weights. The program logs to the console the agents' selected leaders, the true optimal leaders and some other metric.s

```
python3 app.py --formation [0-6]
```
The optional formation flag allows you to specify which formation to run. The default (0) runs all formations.

### Configuring:

**Formations:** to change the formations being tested, add a formation to `data/formations.py`, making sure to follow the existing format.
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
- 5: Rebalance-Flocks

- app.py only supports connected graphs
- plot_optimal only supports connected graphs
to use fw on disconnected graph, return cc then run fw on each

import copy
from helpers.fiedler import fiedler as calc_fiedler

# Currently only supports undirected
# ... but can easly extend to directed

class SpecifySmallStep():
    def __init__(self, g, fiedler_check = calc_fiedler, report_obj = {}):
        self.graph = g
        self.fiedler_check = fiedler_check
        self.report_obj = report_obj

    def is_valid_edge(self, f, target, current, bound,allow_disconnected):
        if not allow_disconnected and f <= 0.001:
            return False
        if bound == "one" and f < target: 
            return False
        if abs(current - target) < abs(f - target):
            return False
        return True

    def fiedler_without_edge(self, g, u, v):
        self.report_obj["considerations_till_arrived"] += 1
        g = copy.deepcopy(g)
        g[u][v] = 0
        g[v][u] = 0
        return self.fiedler_check(g), g

    def find_min_edge(self, g, target, current, bound, allow_disconnected):
        self.report_obj["considerations_till_arrived"] = 0
        l = len(g)
        options = []
        for u in range(l):
            # want to ensure u < v
            # ... to prevent double traversing
            # Modify here to support directed graphs
            for v in range(u + 1, l):
                assert(u < v)
                if g[u][v] == 0: continue
                res = self.fiedler_without_edge(g,u,v)
                options.append(res)
        in_range = list(filter(lambda item: self.is_valid_edge(item[0], target, current, bound,allow_disconnected), options))
        # Take the edge that reduces the Fiedler value the least
        return min(in_range, key=lambda tup: tup[0], default=None)

    def cut_edges(self, target, bound = "two", allow_disconnected = False):
        g = copy.deepcopy(self.graph)
        fiedler = self.fiedler_check(g)

        # Once the following constraints are violated, removing any edge is detrimental
        while fiedler > target and fiedler > 0:
            # print("fiedler ", fiedler)
            res = self.find_min_edge(g, target, fiedler, bound, allow_disconnected)
            if res is None:
                # print("quit")
                break
            f, g_next = res
            fiedler = f
            g = g_next

        return fiedler, g

    def create_graph(self, target, bound = "two", allow_disconnected = False):
        assert(bound == "two" or bound == "one")
        _, g = self.cut_edges(target, bound, allow_disconnected)
        return g
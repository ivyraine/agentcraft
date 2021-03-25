from heapq import heappop, heappush, heappushpop
from math import sqrt
import movement

cardinal_cost = 100
diagonal_cost = 141

class Pathfinding:

    def __init__(self):
        pass


    class Node:
        def __init__(self, pos, g, h, parent, action_to_here, action_cost, legal_actions):
            self.pos = pos
            self.g = g
            self.parent = parent
            self.h = h
            self.f = g + h
            self.parent = parent
            self.action_to_here = action_to_here
            self.action_cost = action_cost
            self.legal_actions = legal_actions

        def __lt__(self, other):  # required for heapq sort
            return self.f < other.f


    def calc_g(self, parent, g_lookup, p_to_c_cost):
        return g_lookup[parent] + p_to_c_cost


    def expand(self, parent : Node, goal, max_x, max_z, legal_actions):  # TODO integtrate legal actions here
        children = []
        x, z = parent.pos
        for n in range(len(legal_actions[x][z])):
            if legal_actions[x][z][n] == False: continue
            dx = movement.directions[n][0]
            dz = movement.directions[n][1]
            tx = parent.pos[0] + dx
            tz = parent.pos[1] + dz
            if (tx < 0 or tz < 0 or tx > max_x or tz > max_z):
                continue
            pos = (tx, tz)
            g = parent.g
            if n < 4:
                g += cardinal_cost
            else:
                g += diagonal_cost
            child = self.Node(
                pos, g, self.heuristic(*pos, *goal), parent,
                action_to_here=(-dx, -dz), action_cost=cardinal_cost, legal_actions=legal_actions[tx][tz]
            )
            children.append(child)
        return children


    def get_path(self, start, end, max_x, max_z, legal_actions):
        first = self.Node(start, g=0, h=self.heuristic(*start, *end), parent=None, action_to_here=None, action_cost=0, legal_actions=legal_actions)
        open = [first]  # heap
        closed = set()
        path = []
        g_lookup = {}
        while len(open) > 0:
            node = heappop(open)
            if node.pos == end:
                return self.backwards_traverse(node, start)
            closed.add(node.pos)
            for child in self.expand(node, end, max_x, max_z, legal_actions):
                p_to_c_cost = child.action_cost
                if child.pos in closed: continue
                if child.pos in open and g_lookup[child] < self.calc_g(node, g_lookup, p_to_c_cost): continue # g is the action cost to get here, parent's g + parent to child g
                g_lookup[child.pos] = child.g
                heappush(open, child)
        return path


    def backwards_traverse(self, node, end):
        curr = node
        path = []
        while curr.pos != end:
            path.append(curr.pos)
            curr = curr.parent
        path.append(curr.pos)
        return path


    def heuristic(self, x1, z1, x2, z2):
        return round(sqrt((x1 - x2) ** 2 + (z1 - z2) ** 2) * cardinal_cost)

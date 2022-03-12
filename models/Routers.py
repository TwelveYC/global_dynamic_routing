import networkx as nx
from queue import PriorityQueue

inf = 1e12


class NodeElement:
    def __init__(self, node, value, last_point):
        self.node = node
        self.value = value
        self.last_point = last_point

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value


def get_path(t, path, node_path, source):
    target = int(t)
    v = path[target]
    if v == source:
        return node_path
    else:
        node_path.append(v)
        get_path(v, path, node_path, source)
    return node_path


def dijkstra_node_source_target(g, w, source, target):
    all_pairs = {}
    n = g.number_of_nodes()

    for i in g.nodes:
        if i != source:
            all_pairs[i] = []

    v = [0 for j in range(n)]
    dis = [inf for j in range(n)]
    paths = ["-1" for j in range(n)]
    for j in nx.neighbors(g, source):
        dis[int(j)] = w[str(source)]
    pq = PriorityQueue()
    pq.put(NodeElement(source, w[str(source)], source))
    while not pq.empty():
        k = pq.get()
        index = int(k.node)
        if v[index]:
            continue
        v[index] = 1
        dis[index] = k.value
        paths[index] = k.last_point
        for j in nx.neighbors(g, k.node):
            pq.put(NodeElement(j, k.value + w[str(j)], k.node))

    result = get_path(target, paths, [target], source)
    result.append(source)
    result.reverse()
    all_pairs[target].extend(result)

    return all_pairs[target]


def dijkstra_node(g, w, source):
    all_pairs = {}
    n = g.number_of_nodes()

    for i in g.nodes:
        if i != source:
            all_pairs[i] = []

    v = [0 for j in range(n)]
    dis = [inf for j in range(n)]
    paths = ["-1" for j in range(n)]
    for j in nx.neighbors(g, source):
        dis[int(j)] = w[str(source)]
    pq = PriorityQueue()
    pq.put(NodeElement(source, w[str(source)], source))
    while not pq.empty():
        k = pq.get()
        index = int(k.node)
        if v[index]:
            continue
        v[index] = 1
        dis[index] = k.value
        paths[index] = k.last_point
        for j in nx.neighbors(g, k.node):
            pq.put(NodeElement(j, k.value + w[str(j)], k.node))
    for target in g.nodes:
        if source != target:
            result = get_path(target, paths, [target], source)
            result.append(source)
            result.reverse()
            all_pairs[target].extend(result)
        else:
            continue
    return all_pairs


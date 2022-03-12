import networkx as nx
import random


class MultiLayerNetwork:
    def __init__(self, graphs, sample_length, couping="assortative"):
        if couping not in ["assortative", "disassortative", "random"]:
            raise NotImplementedError()
        self.graphs = graphs
        self.layers = len(graphs)
        self.couping_model = couping
        self.nodes = []
        for g in self.graphs:
            self.nodes.append(list(g.nodes))
        self.sample_length = sample_length
        self.inner_links, self.couping_A, self.couping_B = self.couping_methods()  # 用来放耦合的边
        self.couping_model = couping
        self.deg = {}
        for i in range(self.layers):
            g = self.graphs[i]
            deg = nx.degree(g)
            self.deg[i] = {}
            for j in deg:
                self.deg[i][j[0]] = j[1]


    def couping_methods(self):
        # 这个函数实现网络不同的耦合方式
        lists = []
        lists_A = []
        lists_B = []
        is_couping = len(self.graphs) == 2
        if is_couping:
            # 如果是随机耦合
            if self.couping_model == "random":
                edge_listA = self.graphs[0].edges
                edge_listB = self.graphs[1].edges
                samplesA = random.sample(edge_listA, self.sample_length)
                samplesB = random.sample(edge_listB, self.sample_length)
                for i in range(self.sample_length):
                    re_order_a = re_order(samplesA[i])
                    re_order_b = re_order(samplesB[i])
                    lists.append([re_order_a, re_order_b])
                    lists_A.append(re_order_a)
                    lists_B.append(re_order_b)
            # 如果是选型耦合
            elif self.couping_model == "assortative":
                becA = nx.centrality.edge_betweenness_centrality(self.graphs[0])
                becB = nx.centrality.edge_betweenness_centrality(self.graphs[1])
                samplesA = sorted(becA.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
                samplesB = sorted(becB.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
                for i in range(self.sample_length):
                    re_order_a = re_order(samplesA[i][0])
                    re_order_b = re_order(samplesB[i][0])
                    lists.append([re_order_a, re_order_b])
                    lists_A.append(re_order_a)
                    lists_B.append(re_order_b)
            # 如果是非选型耦合
            elif self.couping_model == "disassortative":
                becA = nx.centrality.edge_betweenness_centrality(self.graphs[0])
                becB = nx.centrality.edge_betweenness_centrality(self.graphs[1])
                samplesA = sorted(becA.items(), key=lambda kv: (kv[1], kv[0]))
                samplesB = sorted(becB.items(), key=lambda kv: (kv[1], kv[0]))
                for i in range(self.sample_length):
                    re_order_a = re_order(samplesA[i][0])
                    re_order_b = re_order(samplesB[i][0])
                    lists.append([re_order_a, re_order_b])
                    lists_A.append(re_order_a)
                    lists_B.append(re_order_b)
        return lists, lists_A, lists_B


def re_order(e):
    if float(e[0]) > float(e[1]):
        return (e[1], e[0])
    else:
        return e


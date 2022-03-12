import random
import networkx as nx
from random import sample, shuffle
from random import random as rrr
from .Routers import dijkstra_node_source_target
from .MultiLayerNetwork import re_order
import numpy as np
import json



# 局部策略
# lrp 即按照度进行转发
# etar 即按照交通感知进行转发
# integrating local static and dynamic information for routing traffic ilsdi k(n+1)^k
# 全局策略
# sp 即按照最短路径进行转发
# mql 即按照最小排队数目进行转发
# er 即按照最小度进行转发
# mpsi 根据源节点优先级设置有效路由不同的alpha
loc_strategy = ["lrp", "etar", "ilsdi"]
global_strategy = ["sp", "gdr", "er", "mpsi"]
all_strategy = loc_strategy.copy()
all_strategy.extend(global_strategy)



# 可以考虑这样的方法，将路径调理成(较小id， 较大id)然后放入进行判定

class Simulation:
    def __init__(self, net, rs="sp"):
        self.net = net
        self.layer = net.layers
        self.rs = rs
        if self.rs in global_strategy:
            self.is_loc = False
        elif self.rs in loc_strategy:
            self.is_loc = True

        self.packet_dict = {}

        for i in range(self.layer):
            self.packet_dict[i] = {}
            for j in net.nodes[i]:
                self.packet_dict[i][j] = []
        self.net_state = {}
        self.net_total_state = {}
        for i in range(self.layer):
            self.net_state[i] = {}
            self.net_total_state[i] = {}
            for j in net.nodes[i]:
                self.net_state[i][str(j)] = 1
                self.net_total_state[i][str(j)] = 1
        self.packets_numbers = []
        self.efficiency_numbers = []
        v_node = 0
        v_edge = 0
        for i in range(self.layer):
            v_node += self.net.graphs[i].number_of_nodes()
            v_edge += self.net.graphs[i].number_of_edges()
        self.average_degree = 2 * v_edge / v_node

    def step(self):
        links = {0: [], 1: [], "c": []}
        for i in range(self.layer):
            v = self.packet_dict[i].copy()
            k = list(v.keys())
            shuffle(k)
            if i == 0:
                for key in k:
                    ns = v[key]
                    for n in ns:
                        n.time += 1
                        next_link = n.get_next_link()
                        if next_link not in links[i]:
                            is_finish = n.move()
                            if is_finish:
                                self.packet_dict[i][key].remove(n)
                            else:
                                self.packet_dict[i][key].remove(n)
                                self.packet_dict[i][n.loc].append(n)
                                links[i].append(next_link)
                                if next_link in self.net.couping_A:
                                    links["c"].append(self.net.couping_B[self.net.couping_A.index(next_link)])
            elif i == 1:
                for key in k:
                    ns = v[key]
                    for n in ns:
                        n.time += 1
                        next_link = n.get_next_link()
                        if next_link not in links[i] and next_link not in links["c"]:
                            is_finish = n.move()
                            if is_finish:
                                self.packet_dict[i][key].remove(n)
                            else:
                                self.packet_dict[i][key].remove(n)
                                self.packet_dict[i][n.loc].append(n)
                                links[i].append(next_link)

        self.update_state()
        self.get_bandwidth_efficiency(links)

        # 1、新增包
        # 2、按照策略移动所有的包
        # 3、删除到达的包
        # 4、计算序参量
        # 5、计算利用率

    def add_packets(self, packets, layer):
        for i in packets:
            self.packet_dict[layer][i.source].append(i)
        self.update_state()

    def update_state(self):
        # 为了得到较好的效果，对层0来说，需要将对应的层1当中耦合的边节点的包数目加上，得到最终的net state
        for i in range(self.layer):
            for j in self.net.nodes[i]:
                self.net_state[i][str(j)] = len(self.packet_dict[i][j]) + 1
                self.net_total_state[i][str(j)] = self.net_state[i][str(j)]
        if self.layer == 2 :
            for i in range(self.net.sample_length):
                v = self.net.inner_links[i]
                self.net_total_state[0][str(v[0][0])] += self.net_state[1][str(v[1][0])]
                self.net_total_state[0][str(v[0][1])] += self.net_state[1][str(v[1][1])]
                self.net_total_state[1][str(v[1][0])] += self.net_state[0][str(v[0][0])]
                self.net_total_state[1][str(v[1][1])] += self.net_state[0][str(v[0][1])]

    def add_random_packets(self, packets_numbers, layer):
        packets = []
        for i in range(packets_numbers):
            v = sample(self.net.nodes[layer], 2)
            source = v[0]
            target = v[1]
            router = RouterStrategy(self.rs, self.net.graphs[layer], self.net_total_state[layer], layer).get_router(source,
                                                                                                             target)
            packets.append(Packet(router, source, target))
        self.add_packets(packets, layer)

    def get_packet_number(self):
        v = 0
        for i in self.net_state.values():
            v += sum(i.values())
        for i in self.net.graphs:
            v -= i.number_of_nodes()
        return v

    def record_packet_number(self):
        self.packets_numbers.append(self.get_packet_number())

    def get_order_parameter(self, int_packet):
        try:
            return self.average_degree * (self.packets_numbers[-1] - self.packets_numbers[-2]) / int_packet
        except:
            return 0

    def get_bandwidth_efficiency(self, links):
        efficiencies = []
        for i in range(self.layer):
            v = self.net.graphs[i]
            efficiency = len(links[i]) / v.number_of_edges()
            efficiencies.append(efficiency)
        self.efficiency_numbers.append(efficiencies)


class BasicStrategy:
    def __init__(self, method, net, net_state):
        # multi min queue length
        self.net = net
        self.net_state = net_state
        self.method = method
        if method not in all_strategy:
            raise NotImplementedError()


class RouterStrategy(BasicStrategy):
    def __init__(self, method, net, net_state, layer):
        # multi min queue length
        super(RouterStrategy, self).__init__(method, net, net_state)
        self.layer = layer

    def get_router(self, source, target, alpha=1):
        if self.method == "gdr":
            return dijkstra_node_source_target(self.net, self.net_state, source, target)
        else:
            raise NotImplementedError()



class BasePacket:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.loc = source
        self.time = 0
        self.path = 0

    def __str__(self):
        return "source: {}, target: {}, loc: {}".format(self.source, self.target, self.loc)


class Packet(BasePacket):
    def __init__(self, router, source, target):
        super(Packet, self).__init__(source, target)
        self.router = router

    def get_next_link(self):
        next_loc = self.get_next_loc()
        if next_loc >= self.loc:
            return self.loc, next_loc
        else:
            return next_loc, self.loc

    def get_loc(self):
        return self.loc

    def get_next_loc(self):
        if self.loc == self.target:
            raise RuntimeError("已到达终点")
        index = self.router.index(self.loc)
        next_loc = self.router[index + 1]
        return next_loc

    def move(self):
        next_loc = self.get_next_loc()
        self.path += 1
        if next_loc == self.target:
            return True
        else:
            self.loc = next_loc
            return False



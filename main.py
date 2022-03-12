from models.MultiLayerNetwork import MultiLayerNetwork
from models.Simulation import Simulation
import networkx as nx


def main():
    beta= 0.1
    rs = "gdr"
    add_p= 10
    graphs = [
        nx.read_gml("./data/g1_500_4.gml"),
        nx.read_gml("./data/g2_500_4.gml")
    ]
    couping = int(beta * graphs[0].number_of_edges())
    net = MultiLayerNetwork(graphs, couping, couping="random")
    sim = Simulation(net, rs=rs)
    for i in range(3000):
        sim.add_random_packets(add_p, 0)
        sim.add_random_packets(add_p, 1)
        sim.step()
        sim.record_packet_number()
        print(i, sim.packets_numbers[-1])


if __name__ == '__main__':
    main()
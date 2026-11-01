"""Emulated IoT edge network: IoT/attacker side -> gateway (router + IDS) -> server side.

    h1 (10.0.1.10) -- s1 -- gw [10.0.1.1 | 10.0.2.1] -- s2 -- h2 (10.0.2.10)

Run inside WSL as root:
    sudo modprobe -a openvswitch sch_netem
    sudo service openvswitch-switch start
    sudo python3 topology/edge_topo.py          # opens the Mininet CLI
    sudo python3 topology/edge_topo.py --test   # pingall smoke test, then exit
"""
import sys

from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.topo import Topo


class Gateway(Node):
    """Linux router: forwards between the two subnets."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")
        self.cmd("sysctl -w net.ipv4.conf.all.rp_filter=0")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


class EdgeTopo(Topo):
    def build(self):
        s1, s2 = self.addSwitch("s1"), self.addSwitch("s2")
        gw = self.addNode("gw", cls=Gateway, ip="10.0.1.1/24")
        h1 = self.addHost("h1", ip="10.0.1.10/24", defaultRoute="via 10.0.1.1")
        h2 = self.addHost("h2", ip="10.0.2.10/24", defaultRoute="via 10.0.2.1")
        self.addLink(h1, s1)
        self.addLink(gw, s1, intfName1="gw-eth0", params1={"ip": "10.0.1.1/24"})
        self.addLink(gw, s2, intfName1="gw-eth1", params1={"ip": "10.0.2.1/24"})
        self.addLink(h2, s2)


def build_net():
    net = Mininet(topo=EdgeTopo(), switch=OVSBridge, controller=None)
    net.start()
    # Checksum/segmentation offload off, so captured and replayed packets look like the pcaps.
    for node in (net["h1"], net["gw"], net["h2"]):
        for intf in node.intfList():
            if intf.name != "lo":
                node.cmd(f"ethtool -K {intf.name} tx off rx off tso off gso off gro off")
    return net


if __name__ == "__main__":
    setLogLevel("info")
    net = build_net()
    try:
        if "--test" in sys.argv:
            loss = net.pingAll()
            print(f"RESULT pingall loss={loss}%")
        else:
            CLI(net)
    finally:
        net.stop()

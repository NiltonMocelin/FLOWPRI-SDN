#!/usr/bin/python 
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI

c0 = RemoteController('c0', ip='127.0.0.1')

class MyTopo(Topo):
  def __init__(self, **opts):
    Topo.__init__(self, **opts)

    n=3

    s1 = self.addSwitch('s1')
    s2 = self.addSwitch('s2')

    h1 = self.addHost('h1', cpu=.5/n, ip='10.0.0.2')
    h2 = self.addHost('h2', cpu=.5/n, ip='10.0.0.3')
    h3 = self.addHost('h3', cpu=.5/n, ip='10.0.1.2')

    self.addLink(h1, s1, port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(h2, s1, port2=3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)    
    self.addLink(h3, s2, port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(s1, s2, port1=1, port2=1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

def perfTest():
  "Creating Network..."
  topo = MyTopo()
  net = Mininet(topo=topo, controller=c0, link=TCLink, host=CPULimitedHost, switch=OVSKernelSwitch, autoSetMacs=True)
  net.start()
  print ("Dumping...")
  dumpNodeConnections(net.hosts)
  CLI(net)
  net.stop()

if __name__ == '__main__':
  print("Running...")
  setLogLevel('info')
  perfTest()

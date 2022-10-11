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
  def __init__(self, n=3, **opts):
    Topo.__init__(self, **opts)
    s0 = self.addSwitch('s0')
    s1 = self.addSwitch('s1')
    s2 = self.addSwitch('s2')
    s3 = self.addSwitch('s3')

    h1 = self.addHost('h1', cpu=.5/n, ip='10.0.0.1')
    h2 = self.addHost('h2', cpu=.5/n, ip='10.0.0.2')
    h3 = self.addHost('h3', cpu=.5/n, ip='10.0.0.3')

    self.addLink(h1, s0, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(s0, s1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)    
    self.addLink(s1, s3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(s0, s3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(h2, s3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(h3, s3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

def perfTest():
  "Create network and run simple performance test"
  topo = MyTopo(n=3)
  net = Mininet(topo=topo, controller=c0, link=TCLink, host=CPULimitedHost, switch=OVSKernelSwitch)
  net.start()
  print ("Dumping host connections")
  dumpNodeConnections(net.hosts)
  CLI(net)
  net.stop()

if __name__ == '__main__':
  print("Am I runningn!!!")
  setLogLevel('info')
  perfTest()

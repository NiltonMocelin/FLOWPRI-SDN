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

    n=4

    s1 = self.addSwitch('s1')
    s2 = self.addSwitch('s2')
    s3 = self.addSwitch('s3')

    a = self.addHost('a', cpu=.5/n, ip='10.0.0.2')
    b = self.addHost('b', cpu=.5/n, ip='10.0.1.2')
    c = self.addHost('c', cpu=.5/n, ip='10.0.2.2')
    d = self.addHost('d', cpu=.5/n, ip='10.0.2.3')

    self.addLink(b, s2, port2=1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(a, s1, port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)    
    self.addLink(s1, s2, port1=1, port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(s1, s3, port1=3,port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(s3, s2, port1=1, port2=3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(c, s3, port2=3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    self.addLink(d, s3, port2=4, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

def perfTest():
  "Create network and run simple performance test"
  topo = MyTopo()
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

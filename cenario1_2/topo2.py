#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
from mininet.node import CPULimitedHost, OVSKernelSwitch
from mininet.util import dumpNodeConnections


def myNet():

    #RYU_controller
    CONTROLLER_IP='127.0.0.1'

    #net = Mininet( topo=None, build=False)
    net = Mininet(topo=None, build=False, link=TCLink, host=CPULimitedHost, switch=OVSKernelSwitch,autoSetMacs=True)

    hosts=6

    # Create nodes
    h1 = net.addHost( 'h1', mac='01:00:00:00:01:00', cpu=.5/hosts, ip='172.16.10.1/24')
    h2 = net.addHost( 'h2', mac='01:00:00:00:02:00', cpu=.5/hosts, ip='172.16.10.2/24')
    h3 = net.addHost('h3', mac='01:00:00:00:03:00', cpu=.5/hosts, ip='172.16.10.3/24')
    h4 = net.addHost('h4', mac='01:00:00:00:04:00', cpu=.5/hosts, ip='172.16.10.4/24')
    h5 = net.addHost('h5', mac='01:00:00:00:05:00', cpu=.5/hosts, ip='172.16.10.5/24')
    h6 = net.addHost('h6', mac='01:00:00:00:06:00', cpu=.5/hosts, ip='172.16.10.6/24')

    # Create switches
    s1 = net.addSwitch( 's1', listenPort=6634, mac='00:00:00:00:00:01' )
    s2 = net.addSwitch( 's2', listenPort=6635, mac='00:00:00:00:00:02' )

    print ("*** Creating links")
    net.addLink(h1, s1, port2=1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h2, s1, port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h3, s1, port2=3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

    net.addLink(h4, s2, port2=1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h5, s2, port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h6, s2, port2=3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

    net.addLink(s1, s2, port1=4, port2=4, bw=15, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

    # Add Controllers
    c0= net.addController( 'c0', controller=RemoteController, ip=CONTROLLER_IP, port=7000)

    c1 = net.addController( 'c1', controller=RemoteController, ip=CONTROLLER_IP, port=6699)

    net.build()
    net.start()

    # Connect each switch to a different controller
    s1.start( [c0] )
    s2.start( [c1] )

    s1.cmdPrint('ovs-vsctl show')

#    print('Configurando filas\n')
#    s1.cmdPrint("ovs-vsctl -- set port s1-eth4 qos=@newqos -- \
#            --id=@newqos create qos type=linux-htb other-config:max-rate=15000000 queues=0=@q0,1=@q1,2=@q2 -- \
#            --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=2000000 -- \
#            --id=@q1 create queue other-config:min-rate=2000000 other-config:max-rate=5000000 -- \
#            --id=@q2 create queue other-config:min-rate=5000000 other-config:max-rate=15000000")

#    s2.cmdPrint("ovs-vsctl -- set port s2-eth4 qos=@newqos -- \
#            --id=@newqos create qos type=linux-htb other-config:max-rate=15000000 queues=0=@q0,1=@q1,2=@q2 -- \
#            --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=2000000 -- \
#            --id=@q1 create queue other-config:min-rate=2000000 other-config:max-rate=5000000 -- \
#            --id=@q2 create queue other-config:min-rate=5000000 other-config:max-rate=15000000")
    
    print("Mostrando configuracoes queue-bridges porta s1/s2-eth4:\n")
    s1.cmdPrint("tc class list dev s1-eth4")
    s2.cmdPrint("tc class list dev s2-eth4")
    print("\n")

    #remover ?
#    print ("Dumping...")
#    net.start()
    dumpNodeConnections(net.hosts)
    #

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNet()

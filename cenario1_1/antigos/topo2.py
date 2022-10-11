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
#testando ryu controller em um host
#    CONTROLLER_IP_HOST = '172.16.10.1' # assim nao funcionou

    #net = Mininet( topo=None, build=False)
    net = Mininet(topo=None, build=False, link=TCLink, host=CPULimitedHost, switch=OVSKernelSwitch,autoSetMacs=True, ipBase='172.16.10.0/24')

    hosts=4

    # Create nodes
    h1 = net.addHost( 'h1', mac='01:00:00:00:01:00', cpu=.5/hosts, ip='172.16.10.1/24')
    h2 = net.addHost( 'h2', mac='01:00:00:00:02:00', cpu=.5/hosts, ip='172.16.10.2/24')
    h3 = net.addHost('h3', mac='01:00:00:00:03:00', cpu=.5/hosts, ip='172.16.10.3/24')
    h4 = net.addHost('h4', mac='01:00:00:00:04:00', cpu=.5/hosts, ip='172.16.10.4/24')

    # Create switches
    s1 = net.addSwitch( 's1', listenPort=6634, mac='00:00:00:00:00:01', dpid='0000000000000001')
    s2 = net.addSwitch( 's2', listenPort=6635, mac='00:00:00:00:00:02', dpid='0000000000000002')

    print ("*** Creating links")
    net.addLink(h1, s1, port2=1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h2, s1, port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h3, s1, port2=3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

    net.addLink(h4, s2, port2=1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

    net.addLink(s1, s2, port1=4, port2=4, bw=15, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

    #Criar um host no root namespace e linkar com o switch -- sobe o controlador, mas os hosts nao enxergam
    #root = net.addHost('root', inNamespace=False, ip='192.168.123.123')
    #intf = net.addLink(s1,root, port1=5).intf1
    #faltou adicionar as rotas para os hosts - talvez
    #root.cmd( 'route add -net 172.16.10.0/24 dev ' + str( intf ) )

    # Add Controllers
    c0= net.addController( 'c0', controller=RemoteController, ip=CONTROLLER_IP, port=7000)

    c1 = net.addController( 'c1', controller=RemoteController, ip=CONTROLLER_IP, port=6699)

    net.build()
    net.start()

    # Connect each switch to a different controller
    s1.start( [c0] )
    s2.start( [c1] )

    s1.cmdPrint('ovs-vsctl show')
 
    print("\n")

    dumpNodeConnections(net.hosts)

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNet()

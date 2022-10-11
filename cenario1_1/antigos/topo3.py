#!/usr/bin/env python

#adaptacao de sshd.py
#para permitir a comunicacao entre controladores e hosts
# Essa ideia significa conectar o plano de dados com o plano de controle, por isso, uma abordagem eh criar uma rede de controle e uma rede de dados e interligar por meio de um host, que eh criado fora do espaco do mininet mas com um link conectando a um switch.

#Problemas
#1-s1 nao se conecta com o controladory

import sys

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.node import Node, Controller, RemoteController
from mininet.topolib import TreeTopo
from mininet.util import waitListening
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.node import CPULimitedHost, OVSKernelSwitch


#criando uma rede
def Rede():
    net = Mininet(topo=None, build=False, link=TCLink, host=CPULimitedHost, switch=OVSKernelSwitch,autoSetMacs=True, ipBase='172.16.10.0/24')

    hosts=4

    # Create nodes
    h1 = net.addHost( 'h1', mac='01:00:00:00:01:00', cpu=.5/hosts, ip='172.16.10.1/24')
    h2 = net.addHost( 'h2', mac='01:00:00:00:02:00', cpu=.5/hosts, ip='172.16.10.2/24')
    h3 = net.addHost('h3', mac='01:00:00:00:03:00', cpu=.5/hosts, ip='172.16.10.3/24')
    h4 = net.addHost('h4', mac='01:00:00:00:04:00', cpu=.5/hosts, ip='172.16.10.4/24')

    # Create switches
    s1 = net.addSwitch( 's1', listenPort=6634, mac='00:00:00:00:00:01', dpid='0000000000000001')

    # Criando os links
    net.addLink(h1, s1, port2=1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h2, s1, port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h3, s1, port2=3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    
    return net

def connectToRootNS(network, switch, ip, routes):
    #conecta os hosts ao host-root, via switch
    """Connect hosts to root namespace via switch. Starts network.
      network: Mininet() network object
      switch: switch to connect to root namespace
      ip: IP address for root namespace node
      routes: host networks to route to"""

    # Create a node in root namespace and link to switch 0
    root = Node( 'root', inNamespace=False )
    intf = network.addLink( root, switch ).intf1
    root.setIP( ip, intf=intf )
    # Start network that now includes link to root namespace
    
    #conectando o controlador remoto
    c0= net.addController( 'c0', controller=RemoteController, ip=ip, port=7000)
   
    network.build()
    network.start()
    
    s1 = network['s1']
    s1.start( [c0] )

    # Add routes from root ns to hosts
    for route in routes:
        root.cmd( 'route add -net ' + route + ' dev ' + str( intf ) )
    
#mas nao estou interessado em permitir ssh nos hosts
def sshd(network):
    switch = network[ 's1' ]#qual switch vai conectar as redes
    routes = ['172.16.10.0/24'] #aqui complica, no exemplo nao foram alterados os ips e foi posta a rede padrao

    connectToRootNS(network,switch,'10.123.123.1/32', routes)

#    info( "\n*** Hosts are running at the following addresses:\n" )
#    for host in network.hosts:
#        info( host.name, host.IP(), '\n' )
#    info( "\n*** Type 'exit' or control-D to shut down network\n" )

    CLI( network)
    network.stop()

if __name__ == '__main__':
    lg.setLogLevel( 'info')
    net = Rede()
    sshd( net)


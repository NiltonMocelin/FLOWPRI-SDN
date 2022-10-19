#!/usr/bin/env python

"""
Create a network and start sshd(8) on each host.

While something like rshd(8) would be lighter and faster,
(and perfectly adequate on an in-machine network)
the advantage of running sshd is that scripts can work
unchanged on mininet and hardware.

In addition to providing ssh access to hosts, this example
demonstrates:

- creating a convenience function to construct networks
- connecting the host network to the root namespace
- running server processes (sshd in this case) on hosts
"""

import sys

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg, info
from mininet.node import Node, Controller, RemoteController, CPULimitedHost, OVSKernelSwitch
from mininet.topolib import TreeTopo
from mininet.util import waitListening
from mininet.link import TCLink

def TreeNet( depth=1, fanout=2, **kwargs ):
    "Convenience function for creating tree networks."

    net = Mininet(topo=None, build=False, link=TCLink, host=CPULimitedHost, switch=OVSKernelSwitch,autoSetMacs=True, ipBase='172.16.10.0/24')

    hosts=3

    # Create nodes
    h1 = net.addHost( 'h1', mac='01:00:00:00:01:00', cpu=.5/hosts, ip='172.16.10.1/24')
    h2 = net.addHost( 'h2', mac='01:00:00:00:02:00', cpu=.5/hosts, ip='172.16.10.2/24')
    h3 = net.addHost('h3', mac='01:00:00:00:03:00', cpu=.5/hosts, ip='172.16.10.3/24')
#    h4 = net.addHost('h4', mac='01:00:00:00:04:00', cpu=.5/hosts, ip='172.16.10.4/24')

    # Create switches
    s1 = net.addSwitch( 's1', listenPort=6634, mac='00:00:00:00:00:01', dpid='0000000000000001')

    # Criando os links
    net.addLink(h1, s1, port2=1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h2, s1, port2=2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    net.addLink(h3, s1, port2=3, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)

    return net

def connectToRootNS( network, switch, ip, routes ):
    """Connect hosts to root namespace via switch. Starts network.
      network: Mininet() network object
      switch: switch to connect to root namespace
      ip: IP address for root namespace node
      routes: host networks to route to"""
    # Create a node in root namespace and link to switch 0
    root = Node( 'root', inNamespace=False )
    intf = network.addLink( root, switch ).intf1
    root.setIP( ip, intf=intf )

    #conectando o controlador remoto
    c0 = net.addController('c0', controller=RemoteController, ip="127.0.0.1",port=7000)
    s1 = network['s1']
    s1.start( [c0] )

    # Start network that now includes link to root namespace
    network.build()
    network.start()

    s1 = network['s1']
    s1.start( [c0] )

    # Add routes from root ns to hosts
#    for route in routes:
#        root.cmd( 'route add -net ' + route + ' dev ' + str( intf ) )

# pylint: disable=too-many-arguments
def sshd( network, cmd='/usr/sbin/sshd', opts='-D',
          ip='10.123.123.1/32', routes=None, switch=None ):
    """Start a network, connect it to root ns, and run sshd on all hosts.
       ip: root-eth0 IP address in root namespace (10.123.123.1/32)
       routes: Mininet host networks to route to (10.0/24)
       switch: Mininet switch to connect to root namespace (s1)"""
    if not switch:
        switch = network[ 's1' ]  # switch to use
    if not routes:
        routes = [ '172.16.10.0/24' ]
    connectToRootNS( network, switch, ip, routes )
 #   for host in network.hosts:
 #       host.cmd( cmd + ' ' + opts + '&' )
#    info( "*** Waiting for ssh daemons to start\n" )
#    for server in network.hosts:
#        waitListening( server=server, port=22, timeout=5 )

    info( "\n*** Hosts are running sshd at the following addresses:\n" )
    for host in network.hosts:
        info( host.name, host.IP(), '\n' )
    info( "\n*** Type 'exit' or control-D to shut down network\n" )

    CLI( network )
#    for host in network.hosts:
#        host.cmd( 'kill %' + cmd )
    network.stop()


if __name__ == '__main__':
    lg.setLogLevel( 'info')
    net = TreeNet( depth=1, fanout=4 )
    # get sshd args from the command line or use default args
    # useDNS=no -u0 to avoid reverse DNS lookup timeout
    argvopts = ' '.join( sys.argv[ 1: ] ) if len( sys.argv ) > 1 else (
        '-D -o UseDNS=no -u0' )
    sshd( net, opts=argvopts )

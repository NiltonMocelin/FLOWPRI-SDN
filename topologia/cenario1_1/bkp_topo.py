#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI


##TODO:
# Criar os hosts
# Criar os switches
# Criar os links entre eles
# definir os enderecos ip

# setar o protocolo openflow das bridges(switch)
##

# definir as filas e suas configuracoes 
## http://csie.nqu.edu.tw/smallko/sdn/ingress_plicing_queue.html
## https://docs.openvswitch.org/en/latest/faq/qos/?highlight=qos

c0 = RemoteController('c0', ip='127.0.0.1')

class MyTopo(Topo):
  def __init__(self, **opts):
    Topo.__init__(self, **opts)

    n=6
    print("Definindo os switches\n")    
    s1 = self.addSwitch('s1')
    s2 = self.addSwitch('s2')

    hosts = []
    
    print("Definindo os hosts\n")

#    for i in range(1,6):
    for i in range(1,4):
        #hosts conectados a s1
        hosts.append(self.addHost('h'+ str(i), cpu=.5/n, ip='172.16.10.' + str(i)+"/24"))
        print("Setting h"+str(i) + " - ip: 172.16.10."+str(i)+"/24")

#    for i in range(6, 11):
    for i in range(4,7):
        #hosts conectados a s2
        hosts.append(self.addHost('h'+ str(i), cpu=.5/n, ip='172.16.20.' + str(i)+"/24"))
        print("Setting h"+str(i))

    print("pronto\n")
    print("Definindo os links\n")

    #definindo links s1
#    for i in range(0,5):
    for i in range(0,3):
        self.addLink(hosts[i], s1, port2=i+1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
        print("Linking h"+str(i+1) +"<->s1")

    #definindo links s1
#    for i in range(5, 10):
    for i in range(3, 6):
        self.addLink(hosts[i], s2, port2=i-2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
        print("Linking h"+str(i+1) +"<->s2")


    self.addLink(s1, s2, port1=0, port2=0, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    print("pronto\n")


def criarTopo():
  "Creating Network..."
  topo = MyTopo()
  net = Mininet(topo=topo, controller=c0, link=TCLink, host=CPULimitedHost, switch=OVSKernelSwitch, autoSetMacs=True)

  # definindo o openflow das bridges
  print("definindo a versao do openflow das bridges (1.3)")
  s1 = net.get('s1')
  s2 = net.get('s2')
  s1.cmd("ovs-vsctl set Bridge s1 protocols=OpenFlow13")
  s2.cmd("ovs-vsctl set Bridge s2 protocols=OpenFlow13")

  #definir os ips e os gateways dos hosts
  # definir ips das interfaces dos switchs
  s1.cmd("ip addr add 10.0.1.1/24 dev s1-eth0") #interface s1-s2
  s1.cmd("ip addr add 172.16.10.11 dev s1-eth1") #interface s1-h1
  s1.cmd("ip addr add 172.16.10.12 dev s1-eth2") #interface s1-h2
  s1.cmd("ip addr add 172.16.10.13 dev s1-eth3") #interface s1-h3

  s2.cmd("ip addr add 10.0.2.1/24 dev s2-eth0") #interface s2-s1
  s2.cmd("ip addr add 172.16.20.24 dev s2-eth1") #interface s2-h4
  s2.cmd("ip addr add 172.16.20.25 dev s2-eth2") #interface s2-h5
  s2.cmd("ip addr add 172.16.20.26 dev s2-eth3") #interface s2-h6

  # definir o ip correspondente ao gateway para cada host for i in range (x,y): net.get('h'+i).cmd(ip route add default via 0.0.0.0")
  [net.get('h'+str(i)).cmd("ip route add default via 172.16.10.1"+str(i)) for i in range(1,4)]

  [net.get('h'+str(i)).cmd("ip route add default via 172.16.20.2"+str(i)) for i in range(4,7)]




  #definindo as filas 0-2mbps,2-5mbps,5-10mbps
  print("Definindo as filas q0=0-2mbps,q1=2-5mbps,q2=5-10mbps\n")
  s1.cmd("ovs-vsctl -- set port s1-eth0 qos=@newqos -- --id=@newqos create qos type=linux-htb queues=0=@q0,1=@q1,2=@q2 -- --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=2000000 -- --id=@q1 create queue other-config:min-rate=2000000 other-config:max-rate=5000000 -- --id=@q2 create queue other-config:min-rate=5000000 other-config:max-rate=10000000")

  s2.cmd("ovs-vsctl -- set port s2-eth0 qos=@newqos -- --id=@newqos create qos type=linux-htb queues=0=@q0,1=@q1,2=@q2 -- --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=2000000 -- --id=@q1 create queue other-config:min-rate=2000000 other-config:max-rate=5000000 -- --id=@q2 create queue other-config:min-rate=5000000 other-config:max-rate=10000000")

  print("Mostrando configuracoes das bridges:\n")
#  s2.cmd("echo mininet | sudo ovs-vsctl show")
  s1.cmd("ovs-vsctl show")
  print("\n")

  net.start()
  print ("Dumping...")
  dumpNodeConnections(net.hosts)
  
  CLI(net)
  s1.cmd("ovs-vsctl show")
  net.stop()

if __name__ == '__main__':
  print("Running...")
  setLogLevel('info')
  criarTopo()

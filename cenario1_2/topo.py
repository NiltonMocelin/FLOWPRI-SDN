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
## http://csie.nqu.edu.tw/smallko/sdn/ingress_plicing_queue.htm - nao eh html eh htm msm
## https://docs.openvswitch.org/en/latest/faq/qos/?highlight=qos
## https://www.southampton.ac.uk/~drn1e09/ofertie/openflow_qos_mininet.pdf - boa

#filas com tc
## https://tldp.org/HOWTO/Adv-Routing-HOWTO/lartc.qdisc.classful.html
## https://www.southampton.ac.uk/~drn1e09/ofertie/openflow_qos_mininet.pdf

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
        hosts.append(self.addHost('h'+ str(i), cpu=.5/n, ip='172.16.10.' + str(i)+"/24"))
        print("Setting h"+str(i) + " - ip: 172.16.10."+str(i)+"/24")

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

#testando se o bug eh da porta
    self.addLink(s1, s2, port1=4, port2=4)#, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    print("pronto\n")


def criarTopo():
  "Creating Network..."
  topo = MyTopo()
  net = Mininet(topo=topo, controller=c0, link=TCLink, host=CPULimitedHost, switch=OVSKernelSwitch, autoSetMacs=True)

  # definindo o openflow das bridges
#  print("definindo a versao do openflow das bridges (1.3)")
  s1 = net.get('s1')
  s2 = net.get('s2')
#  s1.cmd("ovs-vsctl set Bridge s1 protocols=OpenFlow13")
#  s2.cmd("ovs-vsctl set Bridge s2 protocols=OpenFlow13")

  #definir os ips e os gateways dos hosts
  # definir ips das interfaces dos switchs
#  s1.cmd("ip addr add 10.0.1.1/24 dev s1-eth4") #interface s1-s2
#  s1.cmd("ip addr add 172.16.10.11/24 dev s1-eth1") #interface s1-h1
#  s1.cmd("ip addr add 172.16.10.12/24 dev s1-eth2") #interface s1-h2
#  s1.cmd("ip addr add 172.16.10.13/24 dev s1-eth3") #interface s1-h3

#  s2.cmd("ip addr add 10.0.2.1/24 dev s2-eth4") #interface s2-s1
#  s2.cmd("ip addr add 172.16.10.24/24 dev s2-eth1") #interface s2-h4
#  s2.cmd("ip addr add 172.16.10.25/24 dev s2-eth2") #interface s2-h5
#  s2.cmd("ip addr add 172.16.10.26/24 dev s2-eth3") #interface s2-h6

  # definir o ip correspondente ao gateway para cada host for i in range (x,y): net.get('h'+i).cmd(ip route add default via 0.0.0.0")
#  [net.get('h'+str(i)).cmd("ip route add default via 172.16.10.1"+str(i)) for i in range(1,4)]

#  [net.get('h'+str(i)).cmd("ip route add default via 172.16.10.2"+str(i)) for i in range(4,7)]
  
  #como nao consegui encontrar forma de fazer descoberta de topologia no ryu, e decobrir os enderecos mac e ip de cada interface dos switches.
  #Definir o endereco mac das insterfaces dos switches estaticamente. ex: "ifconfig eth0 hw ether 02:01:02:03:04:08"
#  s1.cmd("ifconfig s1-eth4 hw ether 0A:0A:0A:0A:0A:04")
#  s1.cmd("ifconfig s1-eth1 hw ether 0A:0A:0A:0A:0A:01")
#  s1.cmd("ifconfig s1-eth2 hw ether 0A:0A:0A:0A:0A:02")
#  s1.cmd("ifconfig s1-eth3 hw ether 0A:0A:0A:0A:0A:03")
  
#  s2.cmd("ifconfig s2-eth4 hw ether 02:02:02:02:02:04")
#  s2.cmd("ifconfig s2-eth1 hw ether 02:02:02:02:02:01")
#  s2.cmd("ifconfig s2-eth2 hw ether 02:02:02:02:02:02")
#  s2.cmd("ifconfig s2-eth3 hw ether 02:02:02:02:02:03")


  net.start()
  #definindo as filas 0-2mbps,2-5mbps,5-10mbps
  print("Definindo as filas q0=0-2mbps,q1=2-5mbps,q2=5-10mbps\n")

  ##### obs: ovs-vsctl nao esta configurando as filas aparentemente
#  s1.cmd("ovs-vsctl -- set port s1-eth4 qos=@newqos -- \
#          --id=@newqos create qos type=linux-htb other-config:max-rate=10000000 queues=0=@q0,1=@q1,2=@q2 -- \
#          --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=2000000 -- \
#          --id=@q1 create queue other-config:min-rate=2000000 other-config:max-rate=5000000 -- \
#          --id=@q2 create queue other-config:min-rate=5000000 other-config:max-rate=10000000")

#######  s1.cmd("ovs-vsctl -- set port s1-eth4 qos=@newqos -- --id=@newqos create qos type=linux-htb queues=0=@q0,1=@q1 -- --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=7000000 -- --id=@q1 create queue other-config:min-rate=0 other-config:max-rate=3000000")

#  s2.cmd("ovs-vsctl -- set port s2-eth4 qos=@newqos -- \
#          --id=@newqos create qos type=linux-htb other-config:max-rate=10000000 queues=0=@q0,1=@q1,2=@q2 -- \
#          --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=2000000 -- \
#          --id=@q1 create queue other-config:min-rate=2000000 other-config:max-rate=5000000 -- \
#          --id=@q2 create queue other-config:min-rate=5000000 other-config:max-rate=10000000")

  print("Mostrando configuracoes queue-bridges porta s1/s2-eth4:\n")
  s1.cmd("tc class list dev s1-eth4")
  s2.cmd("tc class list dev s2-eth4")
  print("\n")

#  net.start()
  print ("Dumping...")
  dumpNodeConnections(net.hosts)
  
  CLI(net)
  net.stop()

if __name__ == '__main__':
  print("Running...")
  setLogLevel('info')
  criarTopo()

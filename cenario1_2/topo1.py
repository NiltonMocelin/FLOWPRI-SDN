#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController, OVSSwitch
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

#Conectar multiplos controladores
#https://github.com/mininet/mininet/blob/master/examples/controllers.py
#https://airtoncs.wordpress.com/2016/10/13/how-to-connect-openflow-switches-to-multiple-controllers-mininet/

class MyTopo(Topo):

    n=6

#    net = Mininet(topo=None, build=False)
    net = Mininet(topo=None, build=False, link=TCLink, host=CPULimitedHost, switch=OVSKernelSwitch,autoSetMacs=True)

    print("Definindo os switches\n")    
    s1 = net.addSwitch('s1', listenPort=6634)
    s2 = net.addSwitch('s2', listenPort=6634)

    hosts = []
    
    print("Definindo os hosts\n")

#    for i in range(1,6):
    for i in range(1,4):
        #hosts conectados a s1
        hosts.append(net.addHost('h'+ str(i), cpu=.5/n, ip='172.16.10.' + str(i)+"/24"))
        print("Setting h"+str(i) + " - ip: 172.16.10."+str(i)+"/24")

#    for i in range(6, 11):
    for i in range(4,7):
        #hosts conectados a s2
        hosts.append(net.addHost('h'+ str(i), cpu=.5/n, ip='172.16.10.' + str(i)+"/24"))
        print("Setting h"+str(i) + " - ip: 172.16.10."+str(i)+"/24")

    print("pronto\n")
    print("Definindo os links\n")

    #definindo links s1
#    for i in range(0,5):
    for i in range(0,3):
        net.addLink(hosts[i], s1, port2=i+1, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
        print("Linking h"+str(i+1) +"<->s1")

    #definindo links s2
#    for i in range(5, 10):
    for i in range(3, 6):
        net.addLink(hosts[i], s2, port2=i-2, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
        print("Linking h"+str(i+1) +"<->s2")

#testando se o bug eh da porta
    net.addLink(s1, s2, port1=4, port2=4)#, bw=10, delay='10ms', loss=0, max_queue_size=1000, use_htb=True)
    print("pronto\n")

    #conectando os controllers
    print("Conectando os controllers\n")
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=7000)
    c1 = net.addController('c1', controller=RemoteController, ip='127.0.0.1', port=6699)

    net.build()

    s1.start([c0])
    s2.start([c1])

    s1.cmdPrint('ovs-vsctl show')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    MyTopo()

## topoX.py, utilizar o arquivo com o valor de X maior = ultima versao modificada
s1 - c0 (porta 7000)
s2 - c1 (porta 6699)

# rodar a topologia:
sudo -E python topoX.py

# rodar o controlador
ryu-manager controlador.py --ofp-tcp-listen-port 7000
ryu-manager controlador.py --ofp-tcp-listen-port 6699

# listar portas utilizadas - serve para identificar controladores e ovsdb-server
sudo netstat -tulpn | grep LISTEN


FILAS:
- deletar as filas criadas anteriormente
sh sudo tc qdisc del dev s1-eth1/2/3 root

- adicionar as novas configuracoes de filas
sh tc qdisc add dev s1-eth1/2/3 root handle 1: htb default 1

- adicionar as novas filas
sh tc class add dev s1-eth1 parent 1: classid 1:1 htb rate 1mbit ceil 2mbit (fila 0)

sh tc class add dev s1-eth1 parent 1: classid 1:2 htb rate 4mbit ceil 5mbit (fila 1)


Exemplo experimentado:

Usando apenas o s1, testar as filas 0 e 1 por meio de iperf entre h2(server) e h1

-Pingall, para realizar os arps necessarios

- Delete os fluxos instalados
ovs-ofctl del-flows s1

- Adicione as regras no s1, para observar o efeito de cada fila (obs: substituir os enderecos MAC)
- fila 0 - para fila 1, so alterar o set_queue
sh ovs-ofctl add-flow s1 in_port=1,dl_src=22:ba:be:25:06:7f,dl_dst=3a:42:d1:f1:ef:34,actions=set_queue:0,output=2

sh ovs-ofctl add-flow s1 in_port=2,dl_dst=22:ba:be:25:06:7f,dl_src=3a:42:d1:f1:ef:34,actions=set_queue:0,output=1


#Teste ICMP - foi verificado que mudando o type = 8 (echo request) = 15 (request information). 

Proximo teste -> no packet_in deve ser identificado.




#RESOLVIDO COM UM HOST FORA DO NAMESPACE DO MININET#
# Aparentemente utilizando a ferramenta wsgi eu consigo estabelecer um tipo de comunicacao entre host e controlador
Outra abordagem parece que esta especificada em sshd.py e hwintf.py
2) the basic technique is to add another interface to any mininet node, and connect that interface to the control network

3) take a look at examples/sshd.py and examples/hwintf.py and you should be able to figure it out




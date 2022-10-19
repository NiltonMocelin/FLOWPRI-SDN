#link 10mb

#removendo filas existentes
sudo tc qdisc del dev s1-eth1 root

#adicionando novas filas
sudo tc qdisc add dev s1-eth1 root handle 1: htb default 1

#fila geral
sudo tc class add dev s1-eth1 parent 1: classid 1:1 htb rate 10mbit

#tempo-real
sudo tc class add dev s1-eth1 parent 1:1 classid 1:2 htb rate 3mbit
#dados
sudo tc class add dev s1-eth1 parent 1:1 classid 1:3 htb rate 3mbit
#best-effort
sudo tc class add dev s1-eth1 parent 1:1 classid 1:4 htb rate 2mbit
#controle
sudo tc class add dev s1-eth1 parent 1:1 classid 1:5 htb rate 2mbit 

#adicionando as classes - prio -> In the round-robin process, classes with the lowest priority field are tried for packets first
#rate rate - Maximum rate this class and all its children are guaranteed. Mandatory.

#ceil rate - Maximum  rate  at  which  a  class can send, if its parent has bandwidth to spare.  Defaults to the configured rate,
# which implies no borrowing

#tempo-real
sudo tc class add dev s1-eth1 parent 1:2 classid 1:6 htb rate 3mbit prio 1
sudo tc class add dev s1-eth1 parent 1:2 classid 1:7 htb rate 3mbit prio 2
sudo tc class add dev s1-eth1 parent 1:2 classid 1:8 htb rate 3mbit prio 3

#dados
sudo tc class add dev s1-eth1 parent 1:3 classid 1:9 htb rate 3mbit prio 1
sudo tc class add dev s1-eth1 parent 1:3 classid 1:10 htb rate 3mbit prio 2
sudo tc class add dev s1-eth1 parent 1:3 classid 1:11 htb rate 3mbit prio 3


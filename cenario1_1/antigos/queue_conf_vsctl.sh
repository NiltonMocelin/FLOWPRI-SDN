#
#	        	Hierarquia esperada Em cada porta
#
#  						 	 Fila principal 100% tamanho link
# 
#                                                                        |
#                                                                        |
#                  ______________________________________________________|___________________________________________________
#                 /            /           |             |               |               |                \                  \
#         	 /	      /            |	         |               |               |                 \                  \
#		/            /             |             |               |               |                  \                  \
#	RealPrio10	RealPrio5      RealPrio2    DadosPrio10	     DadosPrio5      DadosPrio2       BestEfforPrio1      ControlePrio1
#PROBLEMA: So ha uma camada de hieraquia possivel, como fazer tudo funcionar gerenciando com o controlador, vai ser um pouco complicado
# Real = 33% -> vou ter que alocar 33% em cada fila da classe Real e pelo controlador fazer com que as 3 filas nao usem mais que 33% + permitido de enfileiramento -> RealPrio10 = 33%, RealPrio5 = 33%, RealPrio2 = 33%
# 
# O mesmo deve valer para dados 35%
# BestEffort = 25%%
# Controle = 7%
#

#esse rate eh em kbps?bps?
#Bem 20 Mbps -> rate = 20000000

sh ovs-vsctl -- set port s1-eth4 qos=@newqos -- --id=@newqos create qos type=linux-htb other-config:max-rate=10000000 queues=0=@q0,1=@q1,2=@q2 -- --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=20000 -- --id=@q1 create queue other-config:min-rate=20000 other-config:max-rate=50000 -- --id=@q2 create queue other-config:min-rate=50000 other-config:max-rate=100000

sh ovs-vsctl -- set port s2-eth4 qos=@newqos -- --id=@newqos create qos type=linux-htb other-config:max-rate=10000000 queues=0=@q0,1=@q1,2=@q2 -- --id=@q0 create queue other-config:min-rate=0 other-config:max-rate=20000 -- --id=@q1 create queue other-config:min-rate=20000 other-config:max-rate=50000 -- --id=@q2 create queue other-config:min-rate=50000 other-config:max-rate=100000

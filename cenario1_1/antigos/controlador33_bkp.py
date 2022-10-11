from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, inet, ether
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
#
from ryu.lib.packet import in_proto
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4, arp, icmp

from ryu.topology import event

#montar grafo da rede
import networkx as nx
import copy

#socket e thread
import socket
from threading import Thread

#tratar json
import json

import copy

from ryu.lib.ovs import vsctl #ovs-vsctl permite conversar com o protocolo OVSDB

############################################
# informacoes armazenadas pelo controlador #
############################################

arpList = {}
contratos = []
contratos_enviar = {}
#self.mac_to_port = {} arrumar esses dois, tirar do controlador e trzer para ca
#self.ip_to_mac = {}
switches = [] #switches administrados pelo controlador

CLASSIFICATION_TABLE = 0 #tabela para marcacao de pacotes
#FILTER_TABLE = 1
FORWARD_TABLE = 2 #tabela para encaminhar a porta destino

CPT = {} #chave (CLASSE,PRIORIDADE,BANDA): valor TOS  

t1 = Thread(target=servidor_socket)
t1.start()

#t1.join()

def servidor_socket():
    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(("10.123.123.1", 4444))
#    tcp.bind(("127.0.1.1", 4444))
#    tcp.bind((socket.gethostbyname(socket.gethostname()),4444))

    print("host:{0} Ouvindo em {1}".format(socket.gethostname(),socket.gethostbyname(socket.gethostname())))

    tcp.listen(5)

    while True:
        conn, addr = tcp.accept()
        print("Connectado: ")
        print(addr)
        print("\n")

        data = conn.recv(1024)
        contrato = json.loads(data)

        print(contrato)

        print("contrato salvo \n")
        contratos.append(contrato)

        #ja criar as regras openflow -> nao se pode pois nao se sabe quais switches estao no caminho (para isso, talvez com bgp ou outro mecanismo, para estabelecer as rotas - entao seria fazivel.

class Regra:
    def __init__(self, ip_src, ip_dst, porta_dst, tos, banda, prioridade, classe, emprestando):
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.porta_dst = porta_dst
        self.tos = tos
        self.emprestando

    def print(self):
        print("src:%s; dst=%s; porta_dst=%d, tos=%s, emprestando=%d" % (self.ip_src, self.ip_dst, self.porta_dst, self.tos, self.empresntando) 

class Porta:
    def __init__(self, name, bandaC1T, bandaC2T, tamanhoFilaC1, tamanhoFilaC2):
        #tamanhoFila = quanto alem da banda posso alocar/emprestar

        #cada fila deve ter uma variavel de controle de largura de banda utilizada e uma variavel de largura de banda total
        self.nome = name
        #a principio o compartilhamento de largura de banda ocorre apenas entre essas duas classes
        #criar os vetores fila da classe 1
        self.c1T = bandaC1T #banda total para esta classe
        self.c1U = 0 #banda utilizada para esta classe
        #fila baixa prioridade 1, classe 1 (tempo real)
        self.p1c1rules = []
        #fila media prioridade 2, classe 1 (tempo real)
        self.p2c1rules = []
        #fila alta prioridade 3, classe 1 (tempo real)
        self.p3c1rules = []

        #criar os vetores fila da classe 2
        self.c2T = bandaC2T
        self.c1U = 0
        #fila baixa prioridade 1, classe 2 (dados)
        self.p1c2rules = []
        #fila media prioridade 2, classe 2 (dados)
        self.p2c2rules = []
        #fila alta prioridade 3, classe 2 (dados)
        self.p3c2rules = []

        #nao eh preciso armazenar informacoes sobre as filas de best-effort e controle de rede

        #O que preciso em cada regra
        #ip_origem
        #ip_destino
        #portalogica_destino?
        #codigo tos (com isso ja sei a largura de banda, a classe e a prioridade)

        #formato das regras json:
        #
        # contrato = {
        #"regra":{
        #    "ip_origem":,
        #    "ip_destino":,
        #    "porta_destino":,
        #    "tos":
        #    }
        #}

    def addRegra(self, ip_src, ip_dst, banda, prioridade, classe, tos, emprestando): #porta = nome da porta

        if classe == 1:
            self.c1U += banda

            if prioridade == 1:
                p1c1rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))
            else if prioridade ==2:
                p2c1rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))
            else: #prioridade ==3
                p3c1rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))
        else: #classe ==2
            self.c2U += banda

            if prioridade == 1:
                p1c2rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))
            else if prioridade ==2:
                p2c2rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))
            else: #prioridade ==3
                p3c2rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))

        return 0

    def delRegra(self, ip_src, ip_dst, tos):
        #busca e remove a regra seja onde estiver - eh dito que nao deve existir duas regras iguais em nenhum lugar ....

        if classe == 1:
            if prioridade == 1:
                
                for i in p1c1rules:
                    if i.ip_src == ip_src and i.ip_dst == ip_dst and i.tos == tos:
                        self.c1U -= i.banda
                        self.p1c1rules.remove(i)
                        return 0
                    
            else if prioridade ==2:
                for i in p2c1rules:
                    if i.ip_src == ip_src and i.ip_dst == ip_dst and i.tos == tos:
                        self.c1U -= i.banda
                        self.p2c1rules.remove(i)
                        return 0


            else: #prioridade ==3
                for i in p3c1rules:
                    if i.ip_src == ip_src and i.ip_dst == ip_dst and i.tos == tos:
                        self.c1U -= i.banda
                        self.p3c1rules.remove(i)
                        return 0

        else: #classe ==2
            if prioridade == 1:
                for i in p1c2rules:
                    if i.ip_src == ip_src and i.ip_dst == ip_dst and i.tos == tos:
                        self.c2U -= i.banda
                        p1c2rules.remove(i)
                        return 0

            else if prioridade ==2:
                for i in p2c2rules:
                    if i.ip_src == ip_src and i.ip_dst == ip_dst and i.tos == tos:
                        self.c2U -= i.banda
                        p2c2rules.remove(i)
                        return 0

            else: #prioridade ==3
                for i in p3c2rules:
                    if i.ip_src == ip_src and i.ip_dst == ip_dst and i.tos == tos:
                        self.c2U -= i.banda
                        p3c2rules.remove(i)
                        return 0

        return -1 #regra nao encontrada

class SwitchOVS:
    def __init__(self, datapath, name, qtdPortas, vetNomePortas, bandaC1T, bandaC2T, tamanhoFilaC1, tamanhoFilaC2): 
                
        self.datapath = datapath
        self.nome = name
        self.portas = []

        #isso faz sentido?
        #Como adicionar itens a um dicionario -> dicio['idade'] = 20
        self.macs = {} #chave: mac, valor: porta
        self.redes = {} #chave: ip, valor: porta
        self.hosts= {} #chave: ip, valor: mac

        #funcoes necessarias:
        #checkBanda - para ver onde posicionar um fluxo (emprestar largura de banda se preciso)
        #addRegra
        #delRegra - deleta a regra por id
        #getRegra - pensar em um identificador para conseguir as regras
        #updateRegras - passa todas um vetor de regras vindos do switch, para atualizar o vetor da classe

  #criar as portas no switch
        for i in range(qtdPortas):
            self.portas.append(Porta(vetNomePortas[i], bandaC1T, bandaC2T, tamanhoFilaC1, tamanhoFilaC2))

        print("\nSwitch %s criado\n" % (name))
    
    def updateRegras(self, nomePorta, regra):
        #pega todas as regras do switch e atualiza na porta nomePorta (poderia atualizar todas as portas do switch jah)
        
#        Flow Removed Message https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html
#       Quando um fluxo expira ou eh removido no switch, este informa o controlador -- se aproveitar desse evento e atualizar as regras do switch !!!!
        print("\nfluxo att na porta %d\n" % (nomePorta))

        return 0

    def getPorta(self, nomePorta):

        for i in self.portas:
            if i.nome == nomePorta:
                return i

    def alocarGBAM(self, nomePorta, origem, destino, banda, prioridade, classe):
 
#       As regras sempre estao atualizadas, pois quando uma eh modificada, essa notifica o controlador, que chama updateRegras        
#        self.updateRegras()# atualizar as regras, pois algumas podem nao estar mais ativas = liberou espaco -- implementar

# o TOS eh decidido aqui dentro, pois dependendo do TOS, pode se definir uma banda, uma prioridade e uma classe
#a classe, a prioridade e a banda sao os atributos originais do fluxo

        porta = self.getPorta(nomePorta)

        if classe == 1:
            if banda <= porta.c1T - porta.c1U: #Total - usado > banda necessaria
                #criar a regra com o TOS = (banda + classe)
                #regra: origem, destino, TOS ?
                tos = "10" #obter do vetor CPT
                porta.addRegra(origem, destino, banda, prioridade, classe, tos, 0)
#                self.addRegra() #ida
#                self.addRegra() #volta


                return 0 #retornar a fila + prioridade = TOS -> procurar o TOS no dicionario CPT


            else: #nao ha banda suficiente, emprestar 
                #verificar se existe fluxo emprestando largura = verificar se alguma regra nas filas da classe está emprestando banda
                emprestando = []
                bandaE = 0

                #sim: somar os fluxos que estao emprestando e ver se a banda eh suficiente para alocar este fluxo 

                for i in porta.p1c1rules:
                    if i.emprestando == 1:
                        emprestando.append(i)

                for i in porta.p2c1rules:
                    if i.emprestando ==1:
                        emprestando.append(i)

                for i in porta.p3c1rules:
                    if i.emprestando ==1:
                        emprestando.append(i)

                contadorE = 0
                for i in emprestando:
                    bandaE += i.banda
                    contadorE+=1

                    if bandaE >= banda:
                        break
                
                if bandaE >= banda:
                    for i in range(contadorE):
                        porta.delRegra(emprestando[i].ip_src, emprestando[i].ip_dst, emprestando[i].tos) #remove a regra da classe switch
                        self.delRegra(emprestando[i].ip_src, emprestando.ip_dst, emprestando[i].tos) #remove a regra no ovswitch

                    
                    #calcular o tos no CPT
                    tos = "10"
                    #sim: remove e aloca.
                    porta.addRegra(ip_src, ip_dst, banda, prioridade, classe, tos, 0) #adiciona na classe
                    self.addRegra(ip_src, ip_dst, banda, prioridade, classe, tos) #adiciona no ovswitch
                    return 0

                
                else:       #nao: testa o nao
                #nao: ver se na outra classe existe espaco para o fluxo
                    if banda <= porta.c2T - porta.c2U:

                        #calcular o tos
                        tos = "10"

                        #sim: alocar este fluxo - emprestando = 1
                        porta.addRegra(Regra(ip_src, ip_Dst, banda, prioridade, 2, tos, 1))            
                        self.addRegra(ip_src, ip_dst, banda, prioridade, classe, tos)
                        return 0


                    else:
                        #nao: verificar na classe original se nao existem fluxos de menor prioridade que somados dao minha banda
                        
                        bandaP = 0
                        remover = []

                                #sim: remove eles e aloca este

                        if prioridade == 3:
    
                            for i in p1c1rules:
                                bandaP += i.banda
                                remover.append(i)

                                if bandaP >= banda:
                                    break

                            if bandaP < banda:
                                for i in p2c1rules:
                                    bandaP += i.banda
                                    remover.append(i)

                                    if bandaP >= banda:
                                        break

                            if bandaP >= banda:
                                for i in remover:
                                    porta.delRegra()
                                    self.delRegra()

                                    porta.addRegra()
                                    self.addRegra()
                                    return 0
                            else:

                                #nao: rejeita o fluxo - criando uma regra de drop por uns 5segundos
                                print("fluxo descartado")
                                return 1

                        else if prioridade == 2:

                            for i in p1c1rules:
                                bandaP += i.banda
                                remover.append(i)

                                if bandaP >= banda:
                                    break

                            if bandaP >= banda:
                                for i in remover:
                                    porta.delRegra()
                                    self.delRegra()

                                porta.addRegra()
                                self.addRegra()
                                return 0
                            else:

                                #nao: rejeita o fluxo - criando uma regra de drop por uns 5segundos
                                print("fluxo descartado")
                                return 1
        
        else:
            if banda <= porta.c2T - porta.c2U: #Total - usado > banda necessaria
                #criar a regra com o TOS = (banda + classe)
                #regra: origem, destino, TOS ?
                tos = "10" #obter do vetor CPT
                porta.addRegra(origem, destino, banda, prioridade, classe, tos, 0)

                return 0 #retornar a fila + prioridade = TOS -> procurar o TOS no dicionario CPT


            else: #nao ha banda suficiente, emprestar 
                #verificar se existe fluxo emprestando largura = verificar se alguma regra nas filas da classe está emprestando banda
                emprestando = []
                bandaE = 0

                #sim: somar os fluxos que estao emprestando e ver se a banda eh suficiente para alocar este fluxo 

                for i in porta.p1c2rules:
                    if i.emprestando == 1:
                        emprestando.append(i)

                for i in porta.p2c2rules:
                    if i.emprestando ==1:
                        emprestando.append(i)

                for i in porta.p3c2rules:
                    if i.emprestando ==1:
                        emprestando.append(i)

                contadorE = 0
                for i in emprestando:
                    bandaE += i.banda
                    contadorE+=1

                    if bandaE >= banda:
                        break
                
                if bandaE >= banda:
                    for i in range(contadorE):
                        porta.delRegra(emprestando[i].ip_src, emprestando[i].ip_dst, emprestando[i].tos) #remove a regra da classe switch
                        self.delRegra(emprestando[i].ip_src, emprestando.ip_dst, emprestando[i].tos) #remove a regra no ovswitch

                    
                    #calcular o tos no CPT
                    tos = "10"
                    #sim: remove e aloca.
                    porta.addRegra(ip_src, ip_dst, banda, prioridade, classe, tos, 0) #adiciona na classe
#                    self.addRegra(match, actions, priority, tabela) #adiciona no ovswitch
                    return 0

                
                else:       #nao: testa o nao
                #nao: ver se na outra classe existe espaco para o fluxo
                    if banda <= porta.c1T - porta.c1U:

                        #calcular o tos
                        tos = "10"

                        #sim: alocar este fluxo - emprestando = 1
                        porta.addRegra(Regra(ip_src, ip_Dst, banda, prioridade, 2, tos, 1))            
                        self.addRegra(ip_src, ip_dst, banda, prioridade, classe, tos)
                        return 0


                    else:
                        #nao: verificar na classe original se nao existem fluxos de menor prioridade que somados dao minha banda
                        
                        bandaP = 0
                        remover = []

                                #sim: remove eles e aloca este

                        if prioridade == 3:
    
                            for i in p1c2rules:
                                bandaP += i.banda
                                remover.append(i)

                                if bandaP >= banda:
                                    break

                            if bandaP < banda:
                                for i in p2c2rules:
                                    bandaP += i.banda
                                    remover.append(i)

                                    if bandaP >= banda:
                                        break

                            if bandaP >= banda:
                                for i in remover:
                                    porta.delRegra()
                                    self.delRegra()

                                    porta.addRegra()
                                    self.addRegra()
                                    return 0
                            else:

                                #nao: rejeita o fluxo - criando uma regra de drop por uns 5segundos
                                print("fluxo descartado")
                                return 1

                        else if prioridade == 2:

                            for i in p1c2rules:
                                bandaP += i.banda
                                remover.append(i)

                                if bandaP >= banda:
                                    break

                            if bandaP >= banda:
                                for i in remover:
                                    porta.delRegra()
                                    self.delRegra()

                                porta.addRegra()
                                self.addRegra()
                                return 0
                            else:

                                #nao: rejeita o fluxo - criando uma regra de drop por uns 5segundos
                                print("fluxo descartado")
                                return 1
              
        return -1

    #criar uma mensagem para remover uma regra de fluxo no ovsswitch
    def delRegra(self, match, actions,tabela):

        #tendo o datapath eh possivel criar pacotes de comando para o switch/datapath
        #caso precise simplificar, pode chamar o cmd e fazer tudo via ovs-ofctl

        #modelo com ovs-ofctl:
        #we can remove all or individual flows from the switch
        #$ sudo ovs-ofctl del-flows <expression>
        #○ ex. $ sudo ovs-ofctl del-flows dp0 dl_type=0x800
        #○ ex. $ sudo ovs-ofctl del-flows dp0 in_port=1
        datapath = self.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = datapath.ofproto_parser.OFPFlowMod(datapath, table_id=table_id, command=ofproto.OFPFC_DELETE,  match=match, instructions=inst)

        datapath.send_msg(mod)

        return 0

    def addRegra(self, match, actions, priority, tabela):
        datapath = self.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=10, match=match, instructions=inst, table_id=table_id)
        datapath.send_msg(mod)

class Dinamico(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        print("Init Start\n")
        super(Dinamico,self).__init__(*args,**kwargs)
        self.mac_to_port = {}
        self.ip_to_mac = {}
        

        print("Init Over\n")
    
#    def __def__(self):
#        print("finalizando thread\n")
#        t1.join()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
#        switch = ev.switch.dp

        print("\n[switch_handler] ")

        print("Switch_id: "+ str(datapath.id) + " conectado: interfaces")
###################################################
###        #criar os switches 
###################################################
        
#        print("\nEventos possiveis?\n")
#        print(ofp_event.__dict__)#printar a classe como um dicionario -> identificar os possiveis eventos

        #obter o numero de portas do switch ?
        qtd_portas = 5
        
        nome_portas = []
        for i in range(5):
            nome_portas.append(str(i))
        
        #para Total = 10 Mb
        bandaC1T=3.3 #33%
        bandaC2T=3.5 #35%

        #para permitir excedente de 10%
        tamanhoFilaC1 = bandaC1T * 0.1 #33 kb
        tamanhoFilaC2 = bandaC2T * 0.1 #35 kb

        switches.append(SwitchOVS(datapath,str(datapath.id), qtd_portas, nome_portas, bandaC1T, bandaC2T, tamanhoFilaC1, tamanhoFilaC2))
        print("\nSwitch criado\n")

###################################################                                                              ###        #criar as filas - executar para este switch um script que vou criar com todas as definicoes das filas.
###################################################


#        print(datapath.address)
#        print(ev.__dict__)

############################################################################################
##########        Criando as regras METER - sao identificadas pelo meter_id      ###########
############################################################################################
        # transformar isso em um for pf
        rates = [4,16,32,64,128,500,1000,2000,4000,8000,10000,20000,25000] #sao 13 meter bands

        for i in range(13):
            #criando meter bands
            bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=rates[i], burst_size=10)]#e esse burst_size ajustar?
            req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=i, bands=bands)
            datapath.send_msg(req)

###########################################################################################
##########        Criar regras TABELA 0 - marcacao e identificacao              ###########
###########################################################################################
        #pacotes sem TOS - sem regras de marcacao e nao sendo icmp information request/reply -> para a tabela 2 (FORWARD)
        #na tabela 2, pacotes sem correspondencia -> enviados para o controlador
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions, FORWARD_TABLE)

        #pacotes com TOS --> envia para a tabela de encaminhamento
        #tabela 0 - classifica os pacotes e envia para a tabela 2
        #criar tabelas https://github.com/knetsolutions/ryu-exercises/blob/master/ex6_multiple_tables.py
        self.add_classification_table(datapath)

        #as demais regras de marcacao sao feitas com base no packet_in e contratos


    def add_flow(self, datapath, priority, match, actions, table_id, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        mod=None

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,priority=priority, match=match, instructions=inst, table_id=table_id)#, table_id = FORWARD_TABLE)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,match=match, instructions=inst, table_id=table_id)#, table_id = FORWARD_TABLE)

#        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,match=match, instructions=inst)
        datapath.send_msg(mod)

########### Testando ############

    def add_classification_table(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionGotoTable(FORWARD_TABLE)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=0, instructions=inst, priority=0) #criando a regra default
        datapath.send_msg(mod)

    def add_forward_table(self, datapath, actions, prioridade):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionGotoTable(FORWARD_TABLE)]
        mod = None
        if actions = None:
            mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE,priority=prioridade, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE,priority=prioridade, instructions=inst, actions=actions)

        datapath.send_msg(mod)
#
#    def apply_filter_table_rules(self, datapath):
#        ofproto = datapath.ofproto
#        parser = datapath.ofproto_parser
#        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ip_proto=in_proto.IPPROTO_TCP)
#        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE,
#                                priority=10000, match=match)
#        datapath.send_msg(mod)


    def _send_packet(self, datapath, port, pkt):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        self.logger.info("To dpid {0} packet-out {1}".format(datapath.id, pkt))
        data = pkt.data
        actions = [parser.OFPActionOutput(port=port)]
        out = parser.OFPPacketOut(datapath=datapath,
                                  buffer_id=ofproto.OFP_NO_BUFFER,
                                  in_port=ofproto.OFPP_CONTROLLER,
                                  actions=actions,
                                  data=data)
        datapath.send_msg(out)

    def send_icmp(self, datapath, srcMac, srcIp, dstMac, dstIp, outPort, seq, data, id=1, type=8, ttl=64):

        e = ethernet.ethernet(dstMac, srcMac, ether.ETH_TYPE_IP)
        iph = ipv4.ipv4(4, 5, 0, 0, 0, 2, 0, ttl, 1, 0, srcIp, dstIp)
#        echo = icmp.echo(id, seq, data)
#        icmph = icmp.icmp(type, 0, 0, echo)

        #icmph = icmp.icmp(15, 0, 0, echo)
        icmph = icmp.icmp(type, 0, 0, data)#pode enviar os dados que quiser, mas tem que ser um vetor binario

        p = packet.Packet()
        p.add_protocol(e)
        p.add_protocol(iph)
        p.add_protocol(icmph)
        p.serialize()

        actions = [datapath.ofproto_parser.OFPActionOutput(outPort)]#no fim tem que ir na fila de controle
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=datapath.ofproto.OFP_NO_BUFFER,
            in_port=100,
            actions=actions,
            data=p.data)
        datapath.send_msg(out)
        return 0


    #Quando um fluxo eh removido ou expirou, chama essa funcao. OBJ --> atualizar quais fluxos não estão mais utilizando banda e remover do switch     
    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_removed_handler(self, ev):
        msg = ev.msg
        dp = msg.datapath
        ofp = dp.ofproto
        
        if msg.reason == ofp.OFPRR_IDLE_TIMEOUT:
            reason = 'IDLE TIMEOUT'
        elif msg.reason == ofp.OFPRR_HARD_TIMEOUT:
            reason = 'HARD TIMEOUT'
        elif msg.reason == ofp.OFPRR_DELETE:
            reason = 'DELETE'
        elif msg.reason == ofp.OFPRR_GROUP_DELETE:
            reason = 'GROUP DELETE'
        else:
            reason = 'unknown'

        self.logger.debug('OFPFlowRemoved received: '
                          'cookie=%d priority=%d reason=%s table_id=%d '
                          'duration_sec=%d duration_nsec=%d '
                          'idle_timeout=%d hard_timeout=%d '
                          'packet_count=%d byte_count=%d match.fields=%s',
                          msg.cookie, msg.priority, reason, msg.table_id,
                          msg.duration_sec, msg.duration_nsec,
                          msg.idle_timeout, msg.hard_timeout,
                          msg.packet_count, msg.byte_count, msg.match)

        in_port = msg.match['in_port']
#        self.updateRegras(portaIn, regra)
        self.updateRegras(in_port, msg)
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        print("[event] Packet_in -- switch: %s\n" % (str(dpid)))

        #####           obter todas as informacoes uteis do pacote          #######
        msg = ev.msg #representa a mensagem packet_in
        dp = msg.datapath #representa o switch
        ofp = dp.ofproto #protocolo openflow na versao implementada pelo switch
        parser = dp.ofproto_parser

        #identificar o switch
        dpid = dp.id
        self.mac_to_port.setdefault(dpid, {})

        #analisar o pacote recebido usando a biblioteca packet
        pkt = packet.Packet(msg.data)

        print("[event] Packet_in -- switch: %s\n" % (str(dpid)))
        print("Cabecalhos:\n")
        for p in pkt.protocols:
            print (p)


        #obter os cabecalhos https://osrg.github.io/ryu-book/en/html/packet_lib.html
        #obter o frame ethernet
        pkt_eth= pkt.get_protocol (ethernet.ethernet)
        if not pkt_eth:
            return

        ##end macs
        dst = pkt_eth.dst
        src = pkt_eth.src


        #end ips
        ip_src = None
        ip_dst = None

        #tipo pacote
        pkt_type = pkt_eth.ethertype

        pkt_ipv4 = pkt.get_protocol(ipv4.ipv4)
        if pkt_ipv4:
            print("\nPacote IPv4: ")
            ip_src = pkt_ipv4.src
            ip_dst = pkt_ipv4.dst

        #obter porta de entrada qual o switch recebeu o pacote
        in_port = msg.match['in_port']


        ########        Aprender informacoes no controlador         ################


        print("\nlistar todos os mac conhecidos")
        print(self.mac_to_port)

        print("\nlistar todos os ips conhecidos")
        print(self.ip_to_mac)

        print("\nlistar todos os contratos conhecidos\n")

        for i in contratos:
            print(i)

        #aprender endereco MAC, evitar flood proxima vez
        self.mac_to_port[dpid][src] = in_port


        #########             ACOES DO CONTROLADOR              ####################
        #Sao 2 forks: i)eh Pacote ICMP? ou ii)NAo

        #i) eh Pacote ICMP - verificar se eh ICMP i.1)Information Request ou i.2)information Reply

        #pkt: responder o arp-> request information + continuar com o arp anterior (replicar)
        pkt_icmp = pkt.get_protocol(icmp.icmp)

        if pkt_icmp:
            print("\nPacote ICMP: \n")
            
#            print(pkt_icmp)
#            print("type = %d" % (pkt_icmp.type))
            if pkt_icmp.type == 15: #request information -> enviar um information reply
                #aqui se for possivel colocar o endereco destino ao qual o fluxo quer alcancar, nos dados do icmp, sera excelente para identificar os contratos que devem ser enviados. para este controlador
                #enviar um information reply:
                #ip-destino: ip_src -> origem pkt-in
                #mac-destino: src -> origem pkt-in (host root do outro controlador)
                #ip-origem: "10.123.123.1" ip do host root (controlador)
                #mac-origem: "00:00:00:00:00:05" mac do host root
                #output_port: in_port -> do pkt-in
                self.send_icmp(dp,"00:00:00:00:00:05", "10.123.123.1",dst, ip_dst, in_port,0,None,1,16,64)
                print("ICMP Information Request -> Replied\n")
                               
                #prosseguir com o icmp para identificar mais controladores
                ### identificar pelo mac eh fraco, tem que haver tbm um mecanismo para identificar a porta de saida pelo ip
                out_port = self.mac_to_port[dpid][dst]
                self.send_icmp(dp, src, ip_src, dst, ip_dst,out_port,0,pkt.data,1,15,64)

            #pkt: responder o arp caso seja para o endereco do controlador-> information reply (enviar os contratos para este controlador)
            if pkt_icmp.type==16 and:

                #enviar os contratos correspondentes para o controlador que respondeu utilizando socket
                print("Enviar os contratos para: ip_dst %s; mac_dst %s; ip_src e mac_src -> host root\n" % (ip_src,mac))

        
        #######         Buscar correspondencia Pkt-in com contratos         ############
              
        print("---------------------------------\n")
        print("procurando match com contratos\n")
        if ip_src != None and ip_dst != None:
             # (1) identificar se o pacote tem match com algum contrato
             for i in contratos:
                 cip_src = i['contrato']['ip_origem']
                 cip_dst = i['contrato']['ip_destino']
                 
                 if cip_src == ip_src and cip_dst == ip_dst:
                     print("match encontrado\n")

                     #encontramos um match com o contrato i
                     #salvar no buffer de envio para os controladores que se referem ao destino cip_dst
                     contratos_enviar[cip_dst]=copy.copy(i) 

                
                     if dst in self.mac_to_port[dpid]:
                         #teste echo request - se funcionar adaptar para o request information
                         
                         out_port = self.mac_to_port[dpid][dst]
                         self.send_icmp(dp, "00:00:00:00:00:05", "10.123.123.1", dst, ip_dst, out_port, 0, None, 1, 15,64)
                          
                         print("icmp enviado enviado - ipdst=%s  portasaida=%d\n" % (ip_dst,out_port))
                         print("---------------------------------\n")

                         #alocar o fluxo switch conforme seus requisitos - verificar em qual fila o fluxo deve ser posicionado
                         #1- Encontrar o switch
                         for i in switches:
                             if i.nome == str(dpid):
                                 #achou o switch

                                 #saber para qual porta deve ser encaminhado --- implementar isso
                                 out_port = 1

                                 #verificar em qual fila da porta posicionar o fluxo
                                 #adicionar a regra na classe switch
                                 #adicionar a regra na tabela do ovsswitch
                                 i.alocarGBAM()                                

                                 return

                        
                 #fluxo nao identificado -> fila de best-effort
                 print("Fluxo nao identificado\n")

                 #criar regra para a fila de best-effort



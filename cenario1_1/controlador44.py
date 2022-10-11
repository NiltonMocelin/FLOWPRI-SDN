#implementar a tabela de roteamento - pode ser estatico msm



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

#cada controlador deve ter o seu
IPC = "10.123.123.1" #IP do root/controlador
MACC = "00:00:00:00:00:05" #MAC do root/controlador

arpList = {}
contratos = []
contratos_enviar = {}
#self.mac_to_port = {} arrumar esses dois, tirar do controlador e trzer para ca
#self.ip_to_mac = {}
switches = [] #switches administrados pelo controlador

CLASSIFICATION_TABLE = 0 #tabela para marcacao de pacotes
FORWARD_TABLE = 2 #tabela para encaminhar a porta destino

CPT = {} #chave (CLASSE,PRIORIDADE,BANDA): valor TOS  
CPF = {} #classe + prioridade = fila
#fila + banda = tos

#banda = valor ; indice = meter_id
RATES = [4,16,32,64,128,500,1000,2000,4000,8000,10000,20000,25000] #sao 13 meter bands

#alimentar o dicionario CPT !!
#tem que criar uma nova tabela no TCC - tabela TOS
#obs: para acessar o TOS -> CPT[(1,1,'1000')]
CPT[(1,1,'1000')] = '0b000101' 
CPT[(2,1,'1000')] = '0b010100' 
CPT[(2,1,'500')] = '0b010111' 
CPT[(2,2,'500')] = '0b011000' 
CPT[(2,3,'500')] = '0b011001' 

CPT[(3,1,'')] = '0b011100' #best-effort
CPT[(4,2,'1000')] = '0b011101' #controle

#CPF - classe + prioridade = fila
CPF[(1,1)] = 0 
CPF[(1,2)] = 1
CPF[(1,3)] = 2
CPF[(2,1)] = 3
CPF[(2,2)] = 4
CPF[(2,3)] = 5
CPF[(3,1)] = 6
CPF[(4,1)] = 7

#BM - banda = meter_id
#MB['']

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

#################
#   INICIANDO SOCKET - RECEBER CONTRATOS
################

t1 = Thread(target=servidor_socket)
t1.start()

#t1.join()




def enviar_contratos(host_ip, host_port, ip_dst_contrato):
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((host_ip, host_port))

    #encontrar os contratos que se referem ao ip_dst informado e enviar para o host_ip:host_port
    for i in contratos:
        if i['contrato']['ip_destino'] == ip_dst_contrato:
            tcp.sendall(json.dumps(contrato).encode())

    tcp.close()


class Regra:
    def __init__(self, ip_src, ip_dst, porta_dst, tos, banda, prioridade, classe, emprestando):
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.porta_dst = porta_dst
        self.tos = tos
        self.emprestando

    def print(self):
        print("src:%s; dst=%s; porta_dst=%d, tos=%s, emprestando=%d" % (self.ip_src, self.ip_dst, self.porta_dst, self.tos, self.empresntando)) 

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
            elif prioridade ==2:
                p2c1rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))
            else: #prioridade ==3
                p3c1rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))
        else: #classe ==2
            self.c2U += banda

            if prioridade == 1:
                p1c2rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))
            elif prioridade ==2:
                p2c2rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))
            else: #prioridade ==3
                p3c2rules.append(Regra(ip_src, ip_dst, tos, banda, prioridade, classe, emprestando))

        return 0

    def delRegra(self, ip_src, ip_dst, tos):
        #busca e remove a regra seja onde estiver - eh dito que nao deve existir duas regras iguais em nenhum lugar ....
        
        keys = [k for k, v in CPT.items() if v == tos]

        classe = k[0]
        prioridade = k[1]
        #banda = [2]

        if classe == 1:
            if prioridade == 1:
                
                for i in p1c1rules:
                    if i.ip_src == ip_src and i.ip_dst == ip_dst and i.tos == tos:
                        self.c1U -= i.banda
                        self.p1c1rules.remove(i)
                        return 0
                    
            elif prioridade ==2:
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

            elif prioridade ==2:
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

    @staticmethod
    def getRules(porta,classe,prioridade):#dado uma porta, classe, prioridade, retornar o vetor ex: p1c1Rules 
        
        if classe == 1:
            if prioridade == 1:
                return porta.p1c1rules
            elif prioridade ==2:
                return porta.p2c1rules
            else:
                return porta.p3c1rules
        else:
            if prioridade == 1:
                return porta.p1c2rules
            elif prioridade ==2:
                return porta.p2c2rules
            else:
                return porta.p3c2rules


    @staticmethod
    def getUT(porta, classe): #dado uma porta, classe, retornar o Total de banda e a banda utilizada pela classe
        if classe == 1:
            return porta.c1U,porta.c1T
        else:
            return porta.c2U,porta.c2T

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
    
    def updateRegras(self, ip_src, ip_dst, tos):
        #pega todas as regras do switch e atualiza na porta nomePorta (poderia atualizar todas as portas do switch jah)
        
#        Flow Removed Message https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html
#       Quando um fluxo expira ou eh removido no switch, este informa o controlador -- se aproveitar desse evento e atualizar as regras do switch !!!!
        print("\n[S%s]UpdateRegras-in\n" % (str(self.nome))

        #na verdade a del regra esta localizando a classe e prioridade por meio do tos, que seria uma tarefa desta funcao update...
        #obter a porta de saida do switch com a tabela de roteamento com base no ip da rede destino  -- que ainda nao foi implementada
        out_port = 1
        porta = self.getPorta(out_port)
        porta.delRegra(ip_src, ip_dst, tos)

        print("[S%s]UpdateRegras-ok-out\n" % (str(self.nome))

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
        
        #para generalizar o metodo GBAM e nao ter de repetir codigo testando para uma classe e depois para outra
        outraClasse = 1
        if classe == 1:
            outraClasse=2

        #banda usada e total na classe original
        cU, cT = Porta.getUT(porta, classe)

        #testando na classe original
        if banda <= cT - cU: #Total - usado > banda necessaria
            #criar a regra com o TOS = (banda + classe)
            #regra: origem, destino, TOS ?
            tos = CPT[(classe, prioridade, banda)] #obter do vetor CPT - sei a classe a prioridade e a banda = tos
            fila = CPF[(classe,prioridade)] #com o tos obter a fila = classe + prioridade
                
            meter_id = 0 #com a banda obter o meter               
            for i in range(13):
                if RATES[i] == banda:
                    meter_id = i
                    break
                
            porta.addRegra(origem, destino, banda, prioridade, classe, tos, 0)
            self.addRegraC(origem, destino, tos)
            self.addRegraF(origem, destino, tos, nomePorta, fila, meter_id, 1)

            return 0 #retornar a fila + prioridade = TOS -> procurar o TOS no dicionario CPT

        else: #nao ha banda suficiente, emprestar 
            #verificar se existe fluxo emprestando largura = verificar se alguma regra nas filas da classe está emprestando banda
            emprestando = []
            bandaE = 0

            #sim: somar os fluxos que estao emprestando e ver se a banda eh suficiente para alocar este fluxo 

            for i in Porta.getRules(porta, classe, 1):
                if i.emprestando == 1:
                    emprestando.append(i)

            for i in Porta.getRules(porta, classe, 2):
                if i.emprestando ==1:
                    emprestando.append(i)

            for i in Porta.getRules(porta, classe, 3):
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
                    self.delRegraF(emprestando[i].ip_src, emprestando.ip_dst, emprestando[i].tos) #remove a regra no ovswitch

                tos = CPT[(classe, prioridade, banda)] #obter do vetor CPT - sei a classe a prioridade e a banda = tos
                fila = CPF[(classe,prioridade)] #com o tos obter a fila = classe + prioridade
                
                meter_id = 0 #com a banda obter o meter               
                for i in range(13):
                    if RATES[i] == banda:
                        meter_id = i
                        break
                
                porta.addRegra(origem, destino, banda, prioridade, classe, tos, 0)
                self.addRegraC(origem, destino, tos)
                self.addRegraF(origem, destino, tos, nomePorta, fila, meter_id, 1)

                return 0

                
            else:       #nao: testa o nao
                #nao: ver se na outra classe existe espaco para o fluxo

                #banda usada e total na outra classe
                cOU, cOT = Porta.getUT(porta, outraClasse)
                if banda <= cOT - cOU:

                    #calcular o tos - neste switch o fluxo sera marcado com um tos diferente do original pois ele precisa emprestar banda de outra classe
                    tos = CPT[(outraClasse, prioridade, banda)] # mudou a classe em que ira ser posicionada, entao muda o tos
                    fila = CPF[(outraClasse,prioridade)] #mudou a classe
                        
                    meter_id = 0
                    for i in range(13):
                        if RATES[i] == banda:
                            meter_id = i
                            break
                
                    #sim: alocar este fluxo - emprestando = 1
                    porta.addRegra(Regra(origem, destino, banda, prioridade, outraClasse, tos, 1))            
                    self.addRegraC(origem, destino, tos)
                    self.addRegraF(origem, destino, tos, nomePorta, fila, meter_id, 1)                        
                    return 0


                else:
                        #nao: verificar na classe original se nao existem fluxos de menor prioridade que somados dao minha banda
                        
                    bandaP = 0
                    remover = []

                                #sim: remove eles e aloca este

                    if prioridade > 1:
    
                        for i in Porta.getRules(porta, classe, 1):
                            bandaP += i.banda
                            remover.append(i)

                            if bandaP >= banda:
                                break
                        
                    if prioridade > 2:
                        if bandaP < banda:
                            for i in Porta.getRules(porta, classe, 2):
                                bandaP += i.banda
                                remover.append(i)

                                if bandaP >= banda:
                                    break

                    if bandaP >= banda:
                        for i in remover:
                            porta.delRegra(i.ip_src, i.ip_dst, i.tos)
                            self.delRegraF(i.ip_src, i.ip_dst, i.tos)

                        #adiciona na classe original
                        tos = CPT[(classe, prioridade, banda)] #obter do vetor CPT - sei a classe a prioridade e a banda = tos
                        fila = CPF[(classe,prioridade)] #com o tos obter a fila = classe + prioridade
                    
                        meter_id = 0 #com a banda obter o meter               
                        for i in range(13):
                            if RATES[i] == banda:
                                meter_id = i
                                break

                        porta.addRegra(Regra(origem, destino, banda, prioridade, classe, tos, 0))            
                        self.addRegraC(origem, destino, tos)
                        self.addRegraF(origem, destino, tos, nomePorta, fila, meter_id, 1)                        
                                
                        return 0

                    else:

                        #nao: rejeita o fluxo - criando uma regra de drop por uns 5segundos
                        print("fluxo descartado")
                        #FAZER NADA - se nao tiver regra, o pacote eh dropado automaticamente.
                        return 1

        #algum erro ocorreu 
        return -1

    #criar uma mensagem para remover uma regra de fluxo no ovsswitch
    def delRegraF(self, ip_src, ip_dst, tos):

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

        match = parser.OFPMatch(eth_type='0x0800', ipv4_src=ip_src, ipv4_dst=ip_dst, ip_dscp=tos)
        mod = datapath.ofproto_parser.OFPFlowMod(datapath, table_id=table_id, command=ofproto.OFPFC_DELETE,  match=match)

        datapath.send_msg(mod)

        return 0

#add regra tabela FORWARD
    def addRegraF(self, ip_src, ip_dst, ip_dscp, out_port, fila, meter_id, flag):
        #https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#flow-instruction-structures
# hardtimeout = 5 segundos # isso eh para evitar problemas com pacotes que sao marcados como best-effort por um contrato nao ter chego a tempo. Assim vou garantir que daqui 5s o controlador possa identifica-lo. PROBLEMA: fluxos geralmente nao duram 5s, mas eh uma abordagem.

        #Para que a regra emita um evento de flow removed, ela precisa carregar uma flag, adicionada no OFPFlowMod
        #flags=ofproto.OFPFF_SEND_FLOW_REM

        datapath = self.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        idletime = 0 # 0 = nao limita
        hardtime = 5 # 5s e some
        prioridade = 10
        match = parser.OFPMatch(eth_type='0x0800', ipv4_src=ip_src, ipv4_dst=ip_dst, ip_dscp=ip_dscp)
        actions = [parser.OFPActionOutput(out_port)]
        inst = [parser.OFPInstructionActions(OFPIT_APPLY_ACTIONS, actions)] # essa instrucao eh necessaria?

        if out_port == 4: #porta que tem fila -- outra maneira para detectar se tem fila seria melhor
            actions = [parser.OFPActionSetQueue(fila), parser.OFPActionOutput(out_port)]
            inst = [parser.OFPInstructionActions(OFPIT_APPLY_ACTIONS, actions)] # essa instrucao eh necessaria?
        
        if meter_id != None:
            inst.append(parser.OFPInstructionMeter(meter_id=meter_id))

        #marcar para gerar o evento FlowRemoved
        if flag == 1:
            mod = parser.OFPFlowMod(datapath=datapath, idle_timeout = idletime, hard_timeout = hardtime, priority=prioridade, match=match, instructions=inst, table_id=FORWARD_TABLE, flags=ofproto.OFPFF_SEND_FLOW_REM)
            datapath.send_msg(mod)
            return

        mod = parser.OFPFlowMod(datapath=datapath, idle_timeout = idletime, hard_timeout = hardtime, priority=prioridade, match=match, instructions=inst, table_id=FORWARD_TABLE)
        datapath.send_msg(mod)

#add regra tabela CLASSIFICATION
    def addRegraC(self, ip_src, ip_dst, ip_dscp):
        #https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#flow-instruction-structures
         #criar regra na tabela de marcacao - obs - utilizar idletime para que a regra suma - serve para que em switches que nao sao de borda essa regra nao exista
                         #obs: cada switch passa por um processo de enviar um packet_in para o controlador quando um fluxo novo chega,assim, com o mecanismo de GBAM, pode ser que pacotes de determinados fluxos sejam marcados com TOS diferentes da classe original, devido ao emprestimo, assim, em cada switch o pacote pode ter uma marcacao - mas com essa regra abaixo, os switches que possuem marcacao diferentes vao manter a regra de remarcacao. Caso ela expire e cheguem novos pacotes, ocorrera novo packet in e o controlador ira executar um novo GBAM - que vai criar uma nova regra de marcacao
                    
        datapath = self.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch(eth_type='0x0800', ipv4_src=ip_src, ipv4_dst=ip_dst)
        actions = [parser.OFPActionSetField(ip_dscp=ip_dscp)]
        inst = [parser.OFPInstructionGotoTable(FORWARD_TABLE), parser.OFPInstructionActions(OFPIT_APPLY_ACTIONS, actions)]
        idletime = 5 # 0 = nao limita
        hardtime = 0 # 5s e some
        prioridade = 10

        mod = parser.OFPFlowMod(datapath=datapath, idle_timeout = idletime, hard_timeout = hardtime, priority=prioridade, match=match, instructions=inst, table_id=tabela)
        datapath.send_msg(mod)

#adicionar rotas no switch - por agora fica com o nome de rede
    def addRede(self, ip_dst, porta): 
        print("[%s]Rede adicionada %s: %s" % (self.nome, ip_dst, porta))
        self.redes[ip_dst]=porta
        return

    def getPortaSaida(self, ip_dst):

        if ip_dst in self.redes:
            return self.redes[ip_dst]

        return None

    def delRede(self, ip_dst, porta):
        print("[%s]Rede deletada %s: %s" % (self.nome, ip_dst, porta))
        return


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

        switch = SwitchOVS(datapath,str(datapath.id), qtd_portas, nome_portas, bandaC1T, bandaC2T, tamanhoFilaC1, tamanhoFilaC2)
        
        #criando a tabela de roteamento - no momento existem apenas 2 switches
        #em breve serao redes separadas
        #switch S1
        if datapath.id == 1:
            switch.addRede('172.16.10.1','1') #rota para destino h1->s1-eth1
            switch.addRede('172.16.10.2','2')
            switch.addRede('172.16.10.3','3')
            switch.addRede('172.16.10.4','4')
            switch.addRede('10.123.123.1','5') #rota para controlador do S1
            switch.addRede('10.123.123.2','4') #rota para controlador do S2



        elif datapath.id == 2:
            #switch S2
            switch.addRede('172.16.10.4','1')
            switch.addRede('172.16.10.1','4')
            switch.addRede('172.16.10.2','4')
            switch.addRede('172.16.10.3','4')
            switch.addRede('10.123.123.1','5') #rota para controlador do S2
            switch.addRede('10.123.123.1','4') #rota para controlador do S1
   
        switches.append(switch)
        print("\nSwitch criado\n")

#        print(datapath.address)
#        print(ev.__dict__)

############################################################################################
##########        Criando as regras METER - sao identificadas pelo meter_id      ###########
############################################################################################
        # transformar isso em um for pf

        for i in range(13):
            #criando meter bands
            bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=RATES[i], burst_size=10)]#e esse burst_size ajustar?
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
        if actions == None:
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
        print('OFPFlowRemoved received switch=%s :: '
                          'cookie=%d priority=%d reason=%s table_id=%d '
                          'duration_sec=%d duration_nsec=%d '
                          'idle_timeout=%d hard_timeout=%d '
                          'packet_count=%d byte_count=%d match.fields=%s \n' % (str(dp.id),
                          msg.cookie, msg.priority, reason, msg.table_id,
                          msg.duration_sec, msg.duration_nsec,
                          msg.idle_timeout, msg.hard_timeout,
                          msg.packet_count, msg.byte_count, msg.match))
       
        ip_src = None
        ip_dst = None
        tos = None
        if 'ipv4_dst' in msg.match:
            ip_dst = msg.match['ipv4_dst']
        if 'ipv4_src' in msg.match:
            ip_src = msg.match['ipv4_src']
        if 'ip_dscp' in msg.match:
            tos= msg.match['ip_dscp']
       
        if ip_src == None or ip_dst == None or tos == None:
            print("Algo deu errado - ip ou tos nao reconhecido\n")
            return 1

        #por agora, tanto as regras de ida quanto as de volta sao marcadas para notificar com o evento
        #atualizar no switch que gerou o evento
        for i in switches:
            if i.nome == str(dp.id):
                i.updateRegras()
                break
        return 0
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

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
        #adaptar essa parte depois, aqui so se quer saber se eh conhecida a porta destino para
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = None


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
                self.send_icmp(dp,MACC, IPC, src, ip_src, in_port,0,None,1,16,64)
                print("ICMP Information Request -> Replied\n")
                               
                #novo icmp para identificar mais controladores - os novos responderao a este controlador e nao ao primeiro
                ### identificar pelo mac eh fraco, tem que haver tbm um mecanismo para identificar a porta de saida pelo ip
                out_port = self.mac_to_port[dpid][dst]
                self.send_icmp(dp, MACC, IPC, dst, ip_dst,out_port,0,pkt.data,1,15,64)

            #pkt: responder o arp caso seja para o endereco do controlador-> information reply (enviar os contratos para este controlador)
            if pkt_icmp.type==16:

                #enviar os contratos correspondentes para o controlador que respondeu utilizando socket
                print("Enviar os contratos para: ip_dst %s; mac_dst %s; ip_src e mac_src -> host root\n" % (ip_src,mac))
                
                #o ip do host destino final, deve estar nos dados do pacote ICMP = nao implementado ainda

                enviar_contratos(ip_dst, 4444, "onde vai estar o ip do host destino?")
                return 0
        
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
                
                     #teste echo request - se funcionar adaptar para o request information
                     self.send_icmp(dp, MACC, IPC, dst, ip_dst, out_port, 0, None, 1, 15,64)
                          
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

                             banda = i['contrato']['banda']
                             prioridade =  i['contrato']['prioridade']
                             classe =  i['contrato']['classe']

                             #ANTES VERIFICAR SE A PORTA POSSUI FILA, se nao, nao adianta utilizar GBAM
                             #IDA
                             if out_port == 4: #por enquanto somente as portas 4 ligam os switches, entao so elas possuem filas
                                 i.alocarGBAM(out_port, ip_src, ip_dst, banda, prioridade, classe)
                             else:
                                 i.addRegraF(ip_src, ip_dst, '', out_port,0,None,0)

                             #VOLTA
                             if in_port == 4:
                                 i.alocarGBAM(in_port, ip_dst, ip_src, banda, prioridade,classe)
                             else:
                                 i.addRegraF(ip_dst, ip_src, '', in_port, 0, None,0)

                             return

                 #fluxo nao identificado -> fila de best-effort
                 print("Fluxo nao identificado\n")

                 #criar a regra de marcacao para este fluxo com o tos de best effort
                 #criar regra para a fila de best-effort (match= {tos, ip_dst} = (meter band + fila=tos) + (porta_saida=ip_dst)
                 #1- Encontrar o switch
                 for i in switches:
                     if i.nome == str(dpid):
                         #achou o switch
                         #criar regra na tabela de encaminhamento

                         #IDA
                         if out_port == 4:
                             i.addRegraF(ip_src, ip_dst, '0b011100', out_port, 6, None,0)
                         else:
                             i.addRegraF(ip_src, ip_dst, '0b01100', out_port, 0, None,0)

                         #VOLTA
                         if in_port == 4:
                             i.addRegraF(ip_dst,ip_src, '0b011100', in_port, 6,None,0) 
                         else:
                             i.addRegraF(ip_dst, ip_src, '0b011100', in_port, 0, None,0)

                         #MARCACAO
                         i.addRegraC(ip_src, ip_dst, '0b011100')

                         return





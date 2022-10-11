from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
#
from ryu.lib.packet import in_proto
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4

#montar grafo da rede
import networkx as nx

arpList = {}


#https://ryu.readthedocs.io/en/latest/library_ovsdb.html - biblioteca ovsdb
#https://tools.ietf.org/html/rfc7047#section-5.2.1 - rfc OVSDB protocolo de gerenciamento - modificar/adicionar/remover filas...
from ryu.lib.ovs import vsctl #ovs-vsctl permite conversar com o protocolo OVSDB

#Cabecalho das classes de protocolo
#https://ryu.readthedocs.io/en/latest/library_packet_ref.html#protocol-header-classes

#ofproto_v1_3_ref
#https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html

#ryubook v1_3
#https://book.ryu-sdn.org/en/Ryubook.pdf

#openflow switch spec v1.3
#https://opennetworking.org/wp-content/uploads/2014/10/openflow-spec-v1.3.0.pdf

#openflow config 1.2
#http://opennetworking.wpengine.com/wp-content/uploads/2013/02/of-config-1.2.pdf

#openflow config 1.1.1
#https://opennetworking.org/wp-content/uploads/2013/02/of-config-1-1-1.pdf

#flowmatch structure
#https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#flow-match-structure

FILTER_TABLE = 5
FORWARD_TABLE = 10

class Dinamico(app_manager.RyuApp): #que ainda nao eh dinamico
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        print("Inint Start\n")
        super(Dinamico,self).__init__(*args,**kwargs)
        self.mac_to_port = {}
        print("Init Over\n")

        #funcao para descoberta de topologia
#    def topologia_descoberta():
#        #implementar uma rotina de descoberta de topologia para montar o grafo
#        return

#    #funcao para criar nova tabela [manter no controlador uma lista de tabelas que podem existir]
#    def tabela_criar():
#        return

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #criar tabelas https://github.com/knetsolutions/ryu-exercises/blob/master/ex6_multiple_tables.py
        self.add_default_table(datapath)
        self.add_filter_table(datapath)
        self.apply_filter_table_rules(datapath)


        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        
        self.add_flow(datapath, 0, match, actions, FORWARD_TABLE, None)

        #recuperar valores de medidores? -- operar sobre eles e enviar mensagem ao switch

        #funcao adicionar fluxo [-- na tabela id_table]
    
    def add_flow(self, datapath, priority, match, actions, table_id, buffer_id):
        return
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        mod=None

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,priority=priority, match=match, instructions=inst, table_id=table_id)#, table_id = FORWARD_TABLE)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,match=match, instructions=inst, table_id=table_id)#, table_id = FORWARD_TABLE)
        datapath.send_msg(mod)

########### Testando ############

    def add_default_table(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionGotoTable(FILTER_TABLE)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=0, instructions=inst)
        datapath.send_msg(mod)

    def add_filter_table(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionGotoTable(FORWARD_TABLE)]
        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE, 
                                priority=1, instructions=inst)
        datapath.send_msg(mod)

    def apply_filter_table_rules(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ip_proto=in_proto.IPPROTO_TCP)
        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE,
                                priority=10000, match=match)
        datapath.send_msg(mod)

###################

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        print("----------------------------")
        print("Packet_in: \n")
        print(ev.__dict__)

        msg = ev.msg #representa a mensagem packet_in
        dp = msg.datapath #representa o switch
        ofp = dp.ofproto #protocolo openflow na versao implementada pelo switch
        parser = dp.ofproto_parser

        print("Msg: ")
        print(msg.__dict__)

        print("----------------------------")

        #identificar o switch
        dpid = dp.id
        self.mac_to_port.setdefault(dpid, {})

        #analisar o pacote recebido usando a biblioteca packet
        pkt = packet.Packet(msg.data)
        print("pkt: ")
        print(pkt.__dict__)
        print("----------------------------")

        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src

        #obter porta de entrada qual o switch recebeu o pacote
        in_port = msg.match['in_port']

        #aprender endereco MAC, evitar flood proxima vez
        self.mac_to_port[dpid][src] = in_port

####
        #responder ARP

        #tratar IPv4
        
####

        #verificar se o MAC destino ja eh conhecido ou se nao, flood
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
            
            #criando regra
            #ida
            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(eth_src=src, eth_dst=dst)
            self.add_flow(dp, 1 ,match, actions, FORWARD_TABLE, None)

            #volta
            actions = [parser.OFPActionOutput(in_port)]
            match = parser.OFPMatch(eth_src = dst, eth_dst = src)
            self.add_flow(dp, 1, match, actions, FORWARD_TABLE, None)

        else:
            out_port = ofp.OFPP_FLOOD
            
            actions = [parser.OFPActionOutput(out_port)]

            #construir o pacote de saida e enviar
            out = parser.OFPPacketOut(datapath=dp,
            buffer_id=ofp.OFP_NO_BUFFER,
            in_port=in_port,
            actions=actions,
            data=msg.data)

            dp.send_msg(out)

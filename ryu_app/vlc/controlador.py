from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet


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

class Dinamico(app_manager.RyuApp): #que ainda nao eh dinamico
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Dinamico,self).__init__(*args,**kwargs)
        self.mac_to_port = {}

        #funcao para descoberta de topologia
        def topologia_descoberta():
            #implementar uma rotina de descoberta de topologia para montar o grafo
            return

        #funcao para criar nova tabela [manter no controlador uma lista de tabelas que podem existir]
        def tabela_criar():
            return

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

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
        self.add_flow(datapath, 0, match, actions)

        #recuperar valores de medidores? -- operar sobre eles e enviar mensagem ao switch

        #funcao adicionar fluxo [-- na tabela id_table]
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

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
        dpid= dp.id
        self.mac_to_port.setdefault(dpid, {})

        #analisar o pacote recebido usando a biblioteca packet
        pkt = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)
        dst = eth_pkt.dst
        src = eth_pkt.src

        #obter porta de entrada qual o switch recebeu o pacote
        in_port = msg.match['in_port']

        #aprender endereco MAC, evitar flood proxima vez
        self.mac_to_port[dpid][src] = in_port

        #verificar se o MAC destino ja eh conhecido ou se nao, flood
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofp.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        #instalar regra
        if out_port != ofp.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(dp, 1 ,match, actions)

        #construir o pacote de saida e enviar
        out = parser.OFPPacketOut(datapath=dp,
        buffer_id=ofp.OFP_NO_BUFFER,
        in_port=in_port,
        actions=actions,
        data=msg.data)

        dp.send_msg(out)

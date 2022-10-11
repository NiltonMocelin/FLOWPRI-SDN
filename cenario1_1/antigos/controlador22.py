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

#tratar json
import json

arpList = {}


from ryu.lib.ovs import vsctl #ovs-vsctl permite conversar com o protocolo OVSDB

CLASSIFICATION_TABLE = 0 #tabela para marcacao de pacotes
#FILTER_TABLE = 1
FORWARD_TABLE = 2 #tabela para encaminhar a porta destino

class Dinamico(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        print("Init Start\n")
        super(Dinamico,self).__init__(*args,**kwargs)
        self.mac_to_port = {}
        self.ip_to_mac = {}

        #adicionar ao mac_to_port e ip_to_mac as informacoes estaticas das interfaces dos switches

        print("Init Over\n")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
#        switch = ev.switch.dp

        print("\n[switch_handler] ")

        print("Switch_id: "+ str(datapath.id) + " conectado: interfaces")
#        print(datapath.address)
#        print(ev.__dict__)

        #tabela 0 - classifica os pacotes e envia para a tabela 2
        #criar tabelas https://github.com/knetsolutions/ryu-exercises/blob/master/ex6_multiple_tables.py
        self.add_classification_table(datapath)

############################################################################################
##########        Criando as regras METER - sao identificadas pelo meter_id      ###########
############################################################################################

        #criando meter band 4kbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=4, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=1, bands=bands)
        datapath.send_msg(req)

        #16kbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=16, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=2, bands=bands)
        datapath.send_msg(req)

        #32kbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=32, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=3, bands=bands)
        datapath.send_msg(req)

        #64kbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=64, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=4, bands=bands)
        datapath.send_msg(req)

        #128kbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=128, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=5, bands=bands)
        datapath.send_msg(req)

        #500kbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=500, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=6, bands=bands)
        datapath.send_msg(req)

        #1mbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=1000, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=7, bands=bands)
        datapath.send_msg(req)

        #2mbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=2000, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=8, bands=bands)
        datapath.send_msg(req)

        #4mbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=4000, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=9, bands=bands)
        datapath.send_msg(req)

        #8mbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=8000, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=10, bands=bands)
        datapath.send_msg(req)

        #10mbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=10000, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=11, bands=bands)
        datapath.send_msg(req)

        #20mbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=20000, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=12, bands=bands)
        datapath.send_msg(req)

        #25mbps
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=25000, burst_size=10)]
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=13, bands=bands)
        datapath.send_msg(req)

        #tabela 2 - dar o matching conforme a porta de saida, e a fila de saida conforme a classe.

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
        self.add_flow(datapath, 0, match, actions, FORWARD_TABLE)


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

#    def add_forward_table(self, datapath):
#        ofproto = datapath.ofproto
#        parser = datapath.ofproto_parser
#        inst = [parser.OFPInstructionGotoTable(FORWARD_TABLE)]
#        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE, 
#                                priority=1, instructions=inst)
#        datapath.send_msg(mod)
#
#    def apply_filter_table_rules(self, datapath):
#        ofproto = datapath.ofproto
#        parser = datapath.ofproto_parser
#        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ip_proto=in_proto.IPPROTO_TCP)
#        mod = parser.OFPFlowMod(datapath=datapath, table_id=FILTER_TABLE,
#                                priority=10000, match=match)
#        datapath.send_msg(mod)


    def responderARP(self, pkt_arp, pkt_eth, in_port, datapath): #retorno 0 = falha; 1= ok
        if pkt_arp.opcode != arp.ARP_REQUEST:
            print("\nnao eh arp-request\n")
            return 0

        dpid = datapath.id

        print("[ARP] respondendo arp-request")
        print ("datapath id: "+str(dpid))
        print ("port: "+str(in_port))
        print ("pkt_eth.dst: " + str(pkt_eth.dst))
        print ("pkt_eth.src: " + str(pkt_eth.src))
        print ("pkt_arp: " + str(pkt_arp))
        print ("pkt_arp:src_ip: " + str(pkt_arp.src_ip))
        print ("pkt_arp:dst_ip: " + str(pkt_arp.dst_ip))
        print ("pkt_arp:src_mac: " + str(pkt_arp.src_mac))
        print ("pkt_arp:dst_mac: " + str(pkt_arp.dst_mac))

        # Destination and source ip address
        d_ip = pkt_arp.dst_ip
        s_ip = pkt_arp.src_ip

        # Destination and source mac address (HW address)
        d_mac = pkt_arp.dst_mac
        s_mac = pkt_arp.src_mac

        #verificar se consigo mapear o ip destino para mac
        mac = self.ip_to_mac.get((dpid,str(d_ip)))

        if mac == None:

            if dpid == 1:
                dpid = 2
            else:
                dpid = 1

            mac = self.ip_to_mac.get((dpid,str(d_ip)))
#            print("[ARP]IP_DST: %s nao possui mac conhecido" % (str(d_ip)))
#            return 0

        if mac == None:
            return


        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet(ethertype=pkt_eth.ethertype,
                                           dst=pkt_eth.src,
                                           src=mac))
        pkt.add_protocol(arp.arp(opcode=arp.ARP_REPLY,
                                 src_mac=mac,
                                 src_ip=d_ip,
                                 dst_mac=pkt_arp.src_mac,
                                 dst_ip=pkt_arp.src_ip))

        self._send_packet(datapath, in_port, pkt)
        print("[ARP] Respondido\n")
        return 1

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


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):


        #pacote chega vindo dos hosts ou de um dominio esterno - verificar os contratos se tem correspondencia
        #verifica qual marcacao deve ser feita, cria regra na tabela CLASSIFICATION_TABLE, para que pacotes end_origem - end_destino, port_origem, port_destino sejam marcados com dscp XXXX e encaminhar para a tabela FORWARD_TABLE
        #neste caso, se eu tivesse multiplas portas de saida, teria de ter multiplas tabelas de encaminhamento, uma para cada porta


#        print("----------------------------")
#        print("Packet_in: \n")
#        print(ev.__dict__)

        msg = ev.msg #representa a mensagem packet_in
        dp = msg.datapath #representa o switch
        ofp = dp.ofproto #protocolo openflow na versao implementada pelo switch
        parser = dp.ofproto_parser

#        print(msg.__dict__)

        print("----------------------------")

        #identificar o switch
        dpid = dp.id
        self.mac_to_port.setdefault(dpid, {})

        #analisar o pacote recebido usando a biblioteca packet
        pkt = packet.Packet(msg.data)
#        print("pkt: ")
#        print(pkt.__dict__)
#        print("event:\n")
#        print(ev.__dict__)

        print("[event] Packet_in -- switch: %s\n" % (str(dpid)))
        print("Cabecalhos:\n")
        for p in pkt.protocols:
            print (p)

        print("\nlistar todos os mac conhecidos")
        print(self.mac_to_port)

        print("\nlistar todos os ips conhecidos")
        print(self.ip_to_mac)

        #obter os cabecalhos https://osrg.github.io/ryu-book/en/html/packet_lib.html
        #obter o frame ethernet
        pkt_eth= pkt.get_protocol (ethernet.ethernet)
        if not pkt_eth:
            return

        ##end macs
        dst = pkt_eth.dst
        src = pkt_eth.src

        #obter porta de entrada qual o switch recebeu o pacote
        in_port = msg.match['in_port']

        #aprender endereco MAC, evitar flood proxima vez
        self.mac_to_port[dpid][src] = in_port

        #end ips
        ip_src = None
        ip_dst = None

        #tipo pacote
        pkt_type = pkt_eth.ethertype

        pkt_arp = pkt.get_protocol (arp.arp)
        if pkt_arp:
            print("\nPacote ARP: ")

            #aprender endereco IP
            ip_src=pkt_arp.src_ip
            ip_dst=pkt_arp.dst_ip
            self.ip_to_mac[(dpid,ip_src)]= src
#            feito = self.responderARP(pkt_arp, pkt_eth, in_port, dp)
#
#            if feito == 1:
#                dst = self.ip_to_mac.get(dpid,str(ip_dst))
#            print(pkt_arp)

        pkt_ipv4 = pkt.get_protocol(ipv4.ipv4)
        if pkt_ipv4:
            print("\nPacote IPv4: ")
            ip_src = pkt_ipv4.src
            ip_dst = pkt_ipv4.dst

#        print("Msg: in_port: %s; ip_src: %s; ip_dst: %s; mac_src: %s; mac_dst: %s; type: %s; proto: %s \n" % (msg.match['in_port'], pkt_ipv4.ip_src, pkt_ipv4.ip_dst, pkt_eth.eth_src, pkt_eth.eth_dst, pkt_eth.eth_type, pkt_ipv4.icmpv4))

        print("----------------------------")

####
        #verificar se o MAC destino ja eh conhecido ou se nao, flood
        if dst in self.mac_to_port[dpid]:

            out_port = self.mac_to_port[dpid][dst]

            print("[nova-regra] ida: eth_src=%s eth_dst=%s; porta saida %s" % (src, dst, out_port))
            print("[nova-regra] volta: eth_src=%s eth_dst=%s; porta saida %s" % (dst, src, in_port))

            #criando regra
            actions = []
            #ida
#            if out_port != 4:
            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(eth_src=src, eth_dst=dst)
            self.add_flow(dp, 5 ,match, actions, FORWARD_TABLE, None)
#            else:
#                actions = [parser.OFPActionOutput(out_port), parser.OFPActionSetQueue(0)]#queue 0 0-2mb
#                match = parser.OFPMatch(eth_src=src, eth_dst=dst)
#                self.add_flow(dp, 5 ,match, actions, FORWARD_TABLE, None)
#
#                actions = [parser.OFPActionOutput(out_port), parser.OFPActionSetQueue(1)]#queue 1 2-5mb
#                match = parser.OFPMatch(eth_src=src, eth_dst=dst, eth_type=ether.ETH_TYPE_IP, ip_proto = inet.IPPROTO_TCP, ip_dscp=25)
#                self.add_flow(dp, 5 ,match, actions, FORWARD_TABLE, None)
#
#                actions = [parser.OFPActionOutput(out_port), parser.OFPActionSetQueue(2)]#queue 2 5-10mb
#                match = parser.OFPMatch(eth_src=src, eth_dst=dst, eth_type=ether.ETH_TYPE_IP, ip_proto = inet.IPPROTO_TCP, ip_dscp=10) #menor taxa de drop
#                self.add_flow(dp, 5 ,match, actions, FORWARD_TABLE, None)



            #volta
            actions = []
#            if in_port != 4:
            actions = [parser.OFPActionOutput(in_port)]
            match = parser.OFPMatch(eth_src=dst, eth_dst=src)
            self.add_flow(dp, 5 ,match, actions, FORWARD_TABLE, None)
#            else:
#                actions = [parser.OFPActionOutput(in_port), parser.OFPActionSetQueue(0)]#queue 0 0-2mb
#                match = parser.OFPMatch(eth_src=dst, eth_dst=src)
#                self.add_flow(dp, 5 ,match, actions, FORWARD_TABLE, None)
#
#                actions = [parser.OFPActionOutput(in_port), parser.OFPActionSetQueue(1)]#queue 1 2-5mb
#                match = parser.OFPMatch(eth_src=dst, eth_dst=src, eth_type=ether.ETH_TYPE_IP, ip_proto = inet.IPPROTO_TCP, ip_dscp=25)
#                self.add_flow(dp, 5 ,match, actions, FORWARD_TABLE, None)
#
#                actions = [parser.OFPActionOutput(in_port), parser.OFPActionSetQueue(2)]#queue 2 5-10mb
#                match = parser.OFPMatch(eth_src=dst, eth_dst=src, eth_type=ether.ETH_TYPE_IP, ip_proto = inet.IPPROTO_TCP, ip_dscp=10) #menor taxa de drop
#                self.add_flow(dp, 5 ,match, actions, FORWARD_TABLE, None)

        else:
            out_port = ofp.OFPP_ALL #por algum motivo o switch nao faz o encaminhamento dos pacotes dessa forma

            print("[flood] mac_dst desconhecido, enviar pacote para:  porta saida %s" % (out_port))


            actions = [parser.OFPActionOutput(out_port)]

            #construir o pacote de saida e enviar
            out = parser.OFPPacketOut(datapath=dp,
            buffer_id=ofp.OFP_NO_BUFFER,
            in_port=in_port,
            actions=actions,
            data=msg.data)

            dp.send_msg(out)

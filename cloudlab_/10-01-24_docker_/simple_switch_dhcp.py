# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#DHCP implementation base: https://github.com/John-Lin/nat/blob/master/dhcp.py
#funcionando !!

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import dhcp
from ryu.lib.packet import ipv4
from ryu.lib.packet import udp
from ryu.lib import addrconv

CONTROLLER_IP = '192.168.255.10'
CONTROLLER_MAC = '08:00:27:c5:74:34'

#Isso cada switch/grupo de switches deve ter o seu
IP_NETWORK = '192.168.255.0'
IP_NETWORK_MASK = '255.255.255.0'
IP_DNS = '0.0.0.0'
dhcp_addr = CONTROLLER_IP
gw_addr = CONTROLLER_IP
dhcp_hw_addr = CONTROLLER_MAC

_LIST_IPS = ['192.168.255.1', '192.168.255.2', '192.168.255.3', '192.168.255.4', '192.168.255.5', '192.168.255.6', '192.168.255.7','192.168.255.8' ]

mac_to_client_ip = {}

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

        self.dhcp_msg_type_code = {
            1: 'DHCP_DISCOVER',
            2: 'DHCP_OFFER',
            3: 'DHCP_REQUEST',
            4: 'DHCP_DECLINE',
            5: 'DHCP_ACK',
            6: 'DHCP_NAK',
            7: 'DHCP_RELEASE',
            8: 'DHCP_INFORM',
        }

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
        
        print(datapath.__dict__)

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

    #dhcp protocol
        #client: dhcpdiscovery broadcast -> : dhcp server
        #Client: <- dhcpoffer unicast : dhcp server
        #client: dhcprequest broadcast -> :dhcp server
        #client: <- dhcpack unicast : dhcp server

    #dhcp reply 
    def send_dhcp_reply(self, datapath, dhcp_pkt):

        msg_dec = dhcp.dhcp.parser(dhcp_pkt.data)
        return

    #dhcp request
    def handle_dhcp_discovery(self, datapath, in_port, dhcp_pkt):

        global mac_to_client_ip
        #melhor fazer isso no packetin msm
        # dhcp_pkt = pkt.get_protocol(dhcp.dhcp)

        # #checar se eh um pacote dhcp 
        # if dhcp_pkt == None:
        #     return

        #identificador do switch
        # datapath.id

        print(dhcp_pkt.__dict__)

        ## montando dhcp_offer
        client_mac = dhcp_pkt.chaddr
        client_ip = dhcp_pkt.ciaddr
        xid = dhcp_pkt.xid
        flags = dhcp_pkt.flags
        hlen = dhcp_pkt.hlen
        hops = dhcp_pkt.hops
        giaddr = dhcp_pkt.giaddr
        yiaddr = _LIST_IPS.pop()
        sname = 'VM-CONTROLLER-001\0'

        #gateway addr os dois 
        dhcp_addr = CONTROLLER_IP
        gw_addr = CONTROLLER_IP
        broadcast_addr = '255.255.255.255'

        ip_network = IP_NETWORK

        dns_addr = '0.0.0.0'
        dhcp_hw_addr = CONTROLLER_MAC

        #obter um ip para o host
        # try:
            # Choose a IP form IP pool list
        client_ip_addr = str(_LIST_IPS.pop())

        mac_to_client_ip[client_mac] = client_ip_addr
        print('AAAAAMAC:%s' % (dhcp_pkt.chaddr))
        # except IndexError:
        #     self.logger.info("EMPTY IP POOL")
        #     return
        
        # send dhcp_offer message.
        dhcp_offer_msg_type = '\x02'
        self.logger.info("Send DHCP message type %s" %
                         (self.dhcp_msg_type_code[ord(dhcp_offer_msg_type)]))


        msg_option = dhcp.option(tag=dhcp.DHCP_MESSAGE_TYPE_OPT,
                                 value=dhcp_offer_msg_type)
        
        options = dhcp.options(option_list=[msg_option])
        hlen = len(addrconv.mac.text_to_bin(dhcp_pkt.chaddr))

        dhcp_pkt = dhcp.dhcp(hlen=hlen,
                             op=dhcp.DHCP_BOOT_REPLY,
                             chaddr=dhcp_pkt.chaddr,
                             yiaddr=client_ip_addr,
                             giaddr=dhcp_pkt.giaddr,
                             xid=dhcp_pkt.xid,
                             options=options)
        
        self._send_dhcp_packet(datapath, dhcp_pkt, CONTROLLER_MAC, CONTROLLER_IP,  in_port)

        return
    
    def handle_dhcp_request(self, dhcp_pkt, datapath, port):
        # send dhcp_ack message.
        dhcp_ack_msg_type = '\x05'
        self.logger.info("Send DHCP message type %s" %
                         (self.dhcp_msg_type_code[ord(dhcp_ack_msg_type)]))

        subnet_option = dhcp.option(tag=dhcp.DHCP_SUBNET_MASK_OPT,
                                    value=addrconv.ipv4.text_to_bin(IP_NETWORK_MASK))
        gw_option = dhcp.option(tag=dhcp.DHCP_GATEWAY_ADDR_OPT,
                                value=addrconv.ipv4.text_to_bin(gw_addr))
        dns_option = dhcp.option(tag=dhcp.DHCP_DNS_SERVER_ADDR_OPT,
                                 value=addrconv.ipv4.text_to_bin(IP_DNS))
        time_option = dhcp.option(tag=dhcp.DHCP_IP_ADDR_LEASE_TIME_OPT,
                                  value='\xFF\xFF\xFF\xFF')
        msg_option = dhcp.option(tag=dhcp.DHCP_MESSAGE_TYPE_OPT,
                                 value=dhcp_ack_msg_type)
        id_option = dhcp.option(tag=dhcp.DHCP_SERVER_IDENTIFIER_OPT,
                                value=addrconv.ipv4.text_to_bin(dhcp_addr))

        options = dhcp.options(option_list=[msg_option, id_option,
                               time_option, subnet_option,
                               gw_option, dns_option])
        hlen = len(addrconv.mac.text_to_bin(dhcp_pkt.chaddr))

        # Look up IP by using client mac address
        print('MAC:%s' % (dhcp_pkt.chaddr))

        #aqui mudei, o certo era apenas consultar pois ja deveria ter passado pelo discovery, mas caso nao tenha passado ainda (ja tenha ip) entao gerar outro ip
        client_ip_addr = '0.0.0.0'
        if dhcp_pkt.chaddr in mac_to_client_ip:
            client_ip_addr = mac_to_client_ip[dhcp_pkt.chaddr]
        else:
            #pronto, registrado
            client_ip_addr = str(_LIST_IPS.pop())
            mac_to_client_ip[dhcp_pkt.chaddr] = client_ip_addr

        dhcp_pkt = dhcp.dhcp(op=dhcp.DHCP_BOOT_REPLY,
                             hlen=hlen,
                             chaddr=dhcp_pkt.chaddr,
                             yiaddr=client_ip_addr,
                             giaddr=dhcp_pkt.giaddr,
                             xid=dhcp_pkt.xid,
                             options=options)

        self._send_dhcp_packet(datapath, dhcp_pkt, CONTROLLER_MAC, CONTROLLER_IP, port)


    def _send_dhcp_packet(self, datapath, dhcp_pkt, mac_src, ip_src, in_port):


        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet
                         (src=mac_src, dst="ff:ff:ff:ff:ff:ff"))
        pkt.add_protocol(ipv4.ipv4
                         (src=ip_src, dst="255.255.255.255", proto=17))
        pkt.add_protocol(udp.udp(src_port=67, dst_port=68))
        pkt.add_protocol(dhcp_pkt)


        print(pkt)

        pkt.serialize()

        data = pkt.data
        actions = [datapath.ofproto_parser.OFPActionOutput(port=in_port)]
        out = datapath.ofproto_parser.OFPPacketOut(datapath=datapath,
                              buffer_id=datapath.ofproto.OFP_NO_BUFFER,
                              in_port=datapath.ofproto.OFPP_CONTROLLER,
                              actions=actions,
                              data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg

        # print(msg.__dict__)

        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]


        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = format(datapath.id, "d").zfill(16)
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)


        ##### if is a dhcp packet
        # udp = eth.get_protocols(udp.udp)[0]
        # if udp.src_port == 67 and udp.dst_port == 68:
        #     handle_dhcp_discovery(datapath, in_port, udp)
        # #####

        dhcpPkt = pkt.get_protocol(dhcp.dhcp)
        if dhcpPkt:
            #verificar o tipo da mensagem
            msgType = ord(dhcpPkt.options.option_list[0].value)
            
            print(msgType)

            print(dhcpPkt.__dict__)
            try:
                self.logger.info("Receive DHCP message type %s" %
                                 (self.dhcp_msg_type_code[msgType]))
            except KeyError:
                self.logger.info("Receive UNKNOWN DHCP message type %d" %
                                 (msgType))
                
            if msgType == dhcp.DHCP_DISCOVER:
                print( 'TIPO111111111111111')
                self.handle_dhcp_discovery(datapath, in_port, dhcpPkt)
            elif msgType == dhcp.DHCP_REQUEST:
                print( '22222222222222222222')
                self.handle_dhcp_request(dhcpPkt, datapath, in_port)
                self.logger.info(mac_to_client_ip)
            else:
                pass

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

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

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import dhcp

CONTROLLER_IP = '192.168.255.0'

_LIST_IPS = ['192.168.1.1', '192.168.1.2', '192.168.1.3']

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

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
    def handle_dhcp_discovery(self, datapath, in_port, pkt):

        dhcp_pkt = pkt.get_protocols(dhcp.dhcp)[0]

        #checar se eh um pacote dhcp 
        if dhcp_pkt == None:
            return

        #identificador do switch
        # datapath.id

        ## montando dhcp_offer
        client_mac = dhcp_pkt['chaddr']
        client_ip = dhcp_pkt['ciaddr']
        xid = dhcp_pkt['xid']
        flags = dhcp_pkt['flags']
        hlen = dhcp_pkt['hlen']
        hops = dhcp_pkt['hops']
        giaddr = dhcp_pkt['giaddr']
        yiaddr = _LIST_IPS.pop()
        sname = 'VM-CONTROLLER-001\0'

        options = dhcp.options()

        dhcp_offer = dhcp.dhcp(op=dhcp.DHCP_OFFER, chaddr= client_mac,options= options,yiaddr=yiaddr, sname=sname, giaddr=giaddr, hops=hops, hlen=hlen, flags=flags, xid=xid, client_ip=client_ip)
        ## fim montagem dhcp_offer

        #montando pacote udp
        e = ethernet.ethernet(dst=dstMac, src=srcMac, ethertype=ether.ETH_TYPE_IP)

        iph = ipv4.ipv4(4, 5, 0, 0, 0, 2, 0, ttl, 1, 0, srcIp, dstIp)

        udp = udp.udp(src_port=67, dst_port=68, total_length=len(dhcp_offer), csum=0)
        udp.serialize(dhcp_offer)

        p = packet.Packet()
        p.add_protocol(e)
        p.add_protocol(iph)
        p.add_protocol(dhcp_offer)
        p.serialize()

        
        actions = [datapath.parser.OFPActionOutput(in_port)]

        out = datapath.parser.OFPPacketOut(datapath=datapath, buffer_id=datapath.ofproto.OFP_NO_BUFFER,
                                  in_port=in_port, actions=actions, data=p.data)

        datapath.send_msg(out)
    #     out = datapath.ofproto_parser.OFPPacketOut(
    # datapath=datapath,
    # buffer_id=datapath.ofproto.OFP_NO_BUFFER,
    # in_port=100,
    # actions=actions,
    # data=p.data)

        return

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

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3


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

class Switch_l2(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(Switch_l2,self).__init__(*args,**kwargs)

        @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
        def packet_in_handler(self, ev):
            msg = ev.msg #representa a mensagem packet_in
            dp = msg.datapath #representa o switch
            ofp = dp.ofproto #protocolo openflow na versao implementada pelo switch
            ofp_parser = dp.ofproto_parser

            actions = [ofp_parser.OFPActionOutput(ofp.OFPP_FLOOD)]

            data = None
            if msg.buffer_id == ofp.OFP_NO_BUFFER:
                data = msg.data

                out = ofp_parser.OFPPacketOut( #packetout constroi a mensagem packet_out
                        datapath=dp,
                        buffer_id=msg.buffer_id,
                        in_port=msg.in_port,
                        actions=actions,
                        data=data)
                dp.send_msg(out)


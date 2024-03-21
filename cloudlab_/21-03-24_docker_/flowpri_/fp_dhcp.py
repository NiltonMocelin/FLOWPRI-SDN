from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import dhcp
from ryu.lib.packet import ipv4
from ryu.lib.packet import udp
from ryu.lib import addrconv
from fp_constants import IPC, MACC

  #dhcp protocol
        #client: dhcpdiscovery broadcast -> : dhcp server
        #Client: <- dhcpoffer unicast : dhcp server
        #client: dhcprequest broadcast -> :dhcp server
        #client: <- dhcpack unicast : dhcp server

### isso tem que ir para outro lugar 

_LIST_IPS = ['192.168.255.1', '192.168.255.2', '192.168.255.3', '192.168.255.4', '192.168.255.5', '192.168.255.6', '192.168.255.7',
            '192.168.255.8','192.168.255.9','192.168.255.11','192.168.255.12','192.168.255.13','192.168.255.14','192.168.255.15',
            '192.168.255.16','192.168.255.17','192.168.255.18','192.168.255.19','192.168.255.20','192.168.255.21' ]

# isso tem que ter o controle de qual switch conecta o host - mac-ip
mac_to_client_ip = {}

CONTROLLER_IP = IPC
CONTROLLER_MAC = MACC

#Isso cada switch/grupo de switches deve ter o seu
IP_NETWORK = '192.168.255.0'
IP_NETWORK_MASK = '255.255.255.0'
IP_DNS = '0.0.0.0'
dhcp_addr = CONTROLLER_IP
gw_addr = CONTROLLER_IP

    #dhcp request
def handle_dhcp_discovery(controller_obj, datapath, in_port, dhcp_pkt):

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
    controller_obj.logger.info("Send DHCP message type %s" %
                    (controller_obj.dhcp_msg_type_code[ord(dhcp_offer_msg_type)]))


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
        
    _send_dhcp_packet(datapath, dhcp_pkt, CONTROLLER_MAC, CONTROLLER_IP,  in_port)

    return
    
def handle_dhcp_request(controller_obj, dhcp_pkt, datapath, port):
    # send dhcp_ack message.
    dhcp_ack_msg_type = '\x05'
    controller_obj.logger.info("Send DHCP message type %s" %
                    (controller_obj.dhcp_msg_type_code[ord(dhcp_ack_msg_type)]))

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

    _send_dhcp_packet(datapath, dhcp_pkt, CONTROLLER_MAC, CONTROLLER_IP, port)


def _send_dhcp_packet(controller_obj, datapath, dhcp_pkt, mac_src, ip_src, in_port):

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

import subprocess


from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3, inet, ether
#from ryu.ofproto import ofproto_v1_5 as ofproto15
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet

from ryu.topology import event

#para configuracoes de queues
from ryu.lib.ovs import bridge
from ryu.lib.ovs import vsctl

from ryu import cfg

CONF = cfg.CONF
CONF.register_opts([
    cfg.IntOpt('ovsdb-timeout', default=2, help='ovsdb timeout')
])
 

# from oslo_config import cfg

# CONF = cfg.ConfigOpts()

# opts = cfg.ListOpt('timeout', default=[10])

# CONF.register_cli_opts(opts)

interface = "s1-eth1"

p = subprocess.Popen("echo mininet | sudo -S tc qdisc del dev s1-eth1 root", stdout=subprocess.PIPE, shell=True)


p = subprocess.Popen("echo mininet | sudo -S tc qdisc del dev " + interface + " root", stdout=subprocess.PIPE, shell=True)

#tentar com apenas a configuracao ovs-vsctl - sem limpar o tcqdisc ---> nao funciona
#ovs-vsctl clear port s1-eth4 qos

#sudo ovs-vsctl show mostra as portas
#obter enderecos do ovsdb sudo ovs-vsctl get-manager
#obter tbm sudo ovs-vsctl show
#setar enderecos para ovsdb sudo ovs-vsctl set-manager "ptcp:6640"
OVSDB_ADDR = 'tcp:127.0.0.1:6640'

#Returns True if the given addr is valid OVSDB server address, otherwise False.
print(vsctl.valid_ovsdb_addr(OVSDB_ADDR))

print("Abrindo conexao com ovsdb server: endereco %s" % (OVSDB_ADDR))
ovs_vsctl = vsctl.VSCtl(OVSDB_ADDR)

command = vsctl.VSCtlCommand('list-br') #funcionando
ovs_vsctl.run_command([command])
print(command)

#sim essa eh a estrutura - feia e com um , a mais quando tiver apenas um parametro
command = vsctl.VSCtlCommand('list-br', ('s1', )) #funcionando
ovs_vsctl.run_command([command])
print(command)

table = "Port"
column = "qos"
command = vsctl.VSCtlCommand('clear', (table, interface, column))

ovs_vsctl.run_command([command])
print(command)

# # command.result[0] is a list of return values
# #deu certo?

#nem com reza - agora foi --> usar o cfg do ryu
#priority nao esta funcionando !!!
# ovs_bridge = bridge.OVSBridge(CONF,1,OVSDB_ADDR)
# queues = [{'priority': '10', 'min-rate': '100000', 'max-rate': '1100000'},{'min-rate':'500000', 'priority': '10'}]
# print(ovs_bridge.set_qos(interface, type='linux-htb', max_rate="15000000", queues=queues))

#estratégia 2: criar as filas e depois modificar a prioridade
#sudo tc class change dev s1-eth1 parent 1:fffe classid 1:1 htb rate 10000000 prio 10


#exemplo
    # def add_tunnel_port(self, name, tunnel_type, remote_ip,
    #                     local_ip=None, key=None, ofport=None):
    #     options = 'remote_ip=%(remote_ip)s' % locals()
    #     if key:
    #         options += ',key=%(key)s' % locals()
    #     if local_ip:
    #         options += ',local_ip=%(local_ip)s' % locals()
 
    #     args = ['Interface', name, 'type=%s' % tunnel_type,
    #             'options:%s' % options]
    #     if ofport:
    #         args.append('ofport_request=%(ofport)s' % locals())
 
    #     command_add = ovs_vsctl.VSCtlCommand('add-port', (self.br_name, name))
    #     command_set = ovs_vsctl.VSCtlCommand('set', args)
    #     self.run_command([command_add, command_set])


# sudo ovs-vsctl -- set port s1-eth4 qos=@newqos -- --id=@newqos create qos type=linux-htb other-config:max-rate=$BANDA queues=0=@q0,1=@q1,2=@q2,3=@q3,4=@q4,5=@q5,6=@q6,7=@q7 -- --id=@q0 create queue other-config:min-rate=$SOMACLASS12 other-config:max-rate=$SOMACLASS12t other-config:priority=10 -- --id=@q1 create queue other-config:min-rate=$SOMACLASS12 other-config:max-rate=$SOMACLASS12t other-config:priority=5 -- --id=@q2 create queue other-config:min-rate=$SOMACLASS12 other-config:max-rate=$SOMACLASS12t other-config:priority=2 -- --id=@q3 create queue other-config:min-rate=$SOMACLASS12 other-config:max-rate=$SOMACLASS12t other-config:priority=10 -- --id=@q4 create queue other-config:min-rate=$SOMACLASS12 other-config:max-rate=$SOMACLASS12t other-config:priority=5 -- --id=@q5 create queue other-config:min-rate=$SOMACLASS12 other-config:max-rate=$SOMACLASS12t other-config:priority=2 -- --id=@q6 create queue other-config:min-rate=$CLASS3 other-config:max-rate=$BANDA other-config:priority=10 -- --id=@q7 create queue other-config:min-rate=$CLASS4 other-config:max-rate=$CLASS4 other-config:priority=2
#nao funcionou
# args = ['Port', 's1-eth1', 'qos=@newqos', '--', '--id=@newqos', 'create', 'qos', 'type=linux-htb', 'other-config:max-rate=15000000', 'queues=0=@q0', '--', '--id=@q0', 'create', 'queue', 'other-config:min-rate=10200000', 'other-config:max-rate=10250000', 'other-config:priority=10']

# command = vsctl.VSCtlCommand('-- set', ('Port', 's1-eth1', 'qos=@newqos', '--', '--id=@newqos', 'create', 'qos', 'type=linux-htb', 'other-config:max-rate=15000000', 'queues=0=@q0', '--', '--id=@q0', 'create', 'queue', 'other-config:min-rate=10200000', 'other-config:max-rate=10250000', 'other-config:priority=10'))
# ovs_vsctl.run_command([command])
# print(command)

#outra forma de configurar ovs-vsctl set interface te-1/1/35 wred_queues:0=@wred1 wred_queues:3=@wred2 -- --id=@wred1 create wred_queue enable=true min_thresh=100 max_thresh=200 drop_probability=50 -- --id=@wred2 create wred_queue enable=true min_thresh=200 max_thresh=400 drop_probability=40

# ovs-vsctl set interface s1-eth1 -- --id=@newqos create qos type=linux-htb other-config:max-rate=15000000 queues=0=@q0 -- --id=@q0 create queue other-config:min-rate=10200000 other-config:max-rate=10250000 other-config:priority=10

command = vsctl.VSCtlCommand('set', ('Interface', 's1-eth1', '--', 'Id=@newqos', 'create', 'qos', 'type=linux-htb', 'other-config:max-rate=15000000', 'queues=0=@q0', '--', 'Id=@q0', 'create', 'queue', 'other-config:min-rate=10200000', 'other-config:max-rate=10250000', 'other-config:priority=10' ))
ovs_vsctl.run_command([command])
print(command)
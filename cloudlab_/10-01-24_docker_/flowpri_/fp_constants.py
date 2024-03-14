from netifaces import AF_INET, ifaddresses, interfaces

#controller singleton
controller_singleton = None

# algumas constantes para o controlador
arpList = {}
contratos = []
contratos_enviar = {}
#self.mac_to_port = {} arrumar esses dois, tirar do controlador e trzer para ca
#self.ip_to_mac = {}

#vetor com os enderecos ip dos controladores conhecidos (enviaram icmps)
controladores_conhecidos = []

switches = [] #switches administrados pelo controlador


#Listar interfaces disponiveis
# print(interfaces())

#cada controlador deve ter o seu
CONTROLLER_INTERFACE = "eth0"

CONTROLADOR_ID = str(CONTROLLER_INTERFACE)
IPC = str(ifaddresses(CONTROLLER_INTERFACE)[AF_INET][0]['addr'])

MACC = str(ifaddresses(CONTROLLER_INTERFACE)[17][0]['addr'])

print("Controlador ID - {}".format(CONTROLADOR_ID))
print("Controlador IP - {}".format(IPC))
print("Controlador MAC - {}".format(MACC))

PORTAC_H = 4444 #porta para receber contratos de hosts
PORTAC_C = 8888 #porta para receber contratos de controladores
PORTAC_X = 9999 #porta para receber arquivos de configuracao json do administrador
PORTAC_ICMP15 = 1115
PORTAC_ICMP16 = 1116

IPV4 = '4'
IPV6 = '41'
ICMPV4 = '1'
ICMPV6 = '58'
TCP = '6'
UDP = '17'
EGP = '8'
IGP = '9'

#service classes
SC_REAL = 1
SC_NONREAL = 2
SC_BEST_EFFORT = 3
SC_CONTROL = 4


FILA_C1P1=0
FILA_C1P2=1
FILA_C1P3=2
FILA_C2P1=3
FILA_C2P2=4
FILA_C2P3=5
FILA_BESTEFFORT=6
FILA_CONTROLE=7

#codigos das acoes
CRIAR=0
REMOVER=1
EMPRESTANDO=1
NAOEMPRESTANDO=0

CLASSIFICATION_TABLE = 0 #tabela para marcacao de pacotes
FORWARD_TABLE = 1 #tabela para encaminhar a porta destino
ALL_TABLES = 255 #codigo para informar que uma acao deve ser tomada em todas as tabelas

CPT = {} #chave (CLASSE,PRIORIDADE,BANDA): valor TOS  
CPF = {} #classe + prioridade = fila
#fila + banda = tos

dhcp_msg_type_code = {
            1: 'DHCP_DISCOVER',
            2: 'DHCP_OFFER',
            3: 'DHCP_REQUEST',
            4: 'DHCP_DECLINE',
            5: 'DHCP_ACK',
            6: 'DHCP_NAK',
            7: 'DHCP_RELEASE',
            8: 'DHCP_INFORM',
 }

#banda = valor ; indice = meter_id
#RATES = [4,16,32,64,128,500,1000,2000,4000,8000,10000,20000,25000] #sao 13 meter bands

#alimentar o dicionario CPT !!
#tem que criar uma nova tabela no TCC - tabela TOS
#obs: para acessar o TOS -> CPT[(1,1,'1000')] 
#obs: dscp = int 8 bits

CPT[('1','1','4')] = 0#'000000'
CPT[('1','1','32')] = 1#'000001'
CPT[('1','1','64')] = 2#'000010'
CPT[('1','1','128')] = 3
CPT[('1','1','500')] = 4
CPT[('1','1','1000')] = 5
CPT[('1','1','2000')] = 6
CPT[('1','1','5000')] = 7
CPT[('1','1','10000')] = 8
CPT[('1','1','25000')] = 9

CPT[('1','2','4')] = 10
CPT[('1','2','32')] = 11
CPT[('1','2','64')] = 12
CPT[('1','2','128')] = 13
CPT[('1','2','500')] = 14
CPT[('1','2','1000')] = 15
CPT[('1','2','2000')] = 16
CPT[('1','2','5000')] = 17
CPT[('1','2','10000')] = 18
CPT[('1','2','25000')] = 19

CPT[('1','3','4')] = 20
CPT[('1','3','32')] = 21
CPT[('1','3','64')] = 22
CPT[('1','3','128')] = 23
CPT[('1','3','500')] = 24
CPT[('1','3','1000')] = 25
CPT[('1','3','2000')] = 26
CPT[('1','3','5000')] = 27
CPT[('1','3','10000')] = 28
CPT[('1','3','25000')] = 29

CPT[('2','1','4')] = 30
CPT[('2','1','32')] = 31
CPT[('2','1','64')] = 32
CPT[('2','1','128')] = 33
CPT[('2','1','500')] = 34
CPT[('2','1','1000')] = 35
CPT[('2','1','2000')] = 36
CPT[('2','1','5000')] = 37
CPT[('2','1','10000')] = 38
CPT[('2','1','25000')] = 39

CPT[('2','2','4')] = 40
CPT[('2','2','32')] = 41
CPT[('2','2','64')] = 42
CPT[('2','2','128')] = 43
CPT[('2','2','500')] = 44
CPT[('2','2','1000')] = 45
CPT[('2','2','2000')] = 46
CPT[('2','2','5000')] = 47
CPT[('2','2','10000')] = 48
CPT[('2','2','25000')] = 49

CPT[('2','3','4')] = 50
CPT[('2','3','32')] = 51
CPT[('2','3','64')] = 52
CPT[('2','3','128')] = 53
CPT[('2','3','500')] = 54
CPT[('2','3','1000')] = 55
CPT[('2','3','2000')] = 56
CPT[('2','3','5000')] = 57
CPT[('2','3','10000')] = 58
CPT[('2','3','25000')] = 59

CPT[('3','1','')] = 60 #'111100' #best-effort
CPT[('4','2','1000')] = 61 #'111101' #controle

#CPF - classe + prioridade = fila
CPF[(1,1)] = 0 
CPF[(1,2)] = 1
CPF[(1,3)] = 2
CPF[(2,1)] = 3
CPF[(2,2)] = 4
CPF[(2,3)] = 5
CPF[(3,1)] = 6
CPF[(4,1)] = 7
#codigo para enviar arquivos de configuracao para o controlador

import socket
import sys #para usar os parametros por linha de comando
import json
#lidar com bytes
import struct
#coletar tempo
import time
from os.path import exists

#alterado para o endereco ip ficticio do controlador
HOST="10.10.10.1"
#HOST="127.0.1.1"
PORT= 9999
file="nada.json"

if len(sys.argv) < 3:
    print("[erro-modo de usar->] python cfg_cli.py <ip_controlador> <arquivo_config.json>\n")
    exit(0)

file = sys.argv[2]

HOST = sys.argv[1]

#algoritmo:
#1- verificar se o arquivo de cfg existe
#2- ler todo o conteudo
#3- tentar montar um json aqui
#4- se nao montar um json corretamente -> informar e sair
#5- se montar um json corretamente -> enviar ao controlador

######

#1- verificar se o arquivo de cfg existe
if(format(exists(file)) == False):
    print("Arquivo {} nao encontrado na pasta raiz\n".format(file))
    exit(0)        


texto = open(file, "r")

#2 e 3- tentar montar um json aqui
cfg_json=json.load(texto)
cfg_bytes = json.dumps(cfg_json).encode('utf-8')

qtdBytes = struct.pack('<i',len(cfg_bytes))

print("printando json\n")
print(cfg_json)

#4- se nao montar um json corretamente -> informar e sair
# if "addswitch" not in cfg_json:
#     print("aquivo invalido")
#     exit(0)

#5- se montar um json corretamente -> enviar ao controlador
print("Enviando cfg para -> HOST:%s, PORT: %d\n" % (HOST,PORT))

#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect((HOST, PORT))

print("host: enviando contrato %d\n" %(round(time.monotonic() * 1000)))
tcp.send(qtdBytes)
tcp.send(cfg_bytes)

tcp.close()

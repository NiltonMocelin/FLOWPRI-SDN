import socket
import sys #para usar os parametros por linha de comando
import json

#HOST="10.123.123.1"
HOST="127.0.1.1"
PORT= 4444

#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect((HOST, PORT))

#n = int(sys.argv[1]) #obtem o primeiro parametro da entrada
#
#Contrato json - tem que ir melhorando esse contrato, se usar a porta origem e destino fica mais -preciso- pq nao generaliza um contrato para um ip mas para um ip+porta. - aqui eh um teste, por isso nao usa portas -
#
# {
#   "contrato":{
#   "ip_origem":"172.16.10.1",
#   "ip_destino":"172.16.10.2",
#   "banda":"10000", #em kbps
#   "prioridade":"1",
#   "classe":"0" #0=tempo-real,1=dados,2=nao classificado,3=controle
#   }
# }
#
contrato = {
        "contrato":{
            "ip_origem":sys.argv[1],
            "ip_destino":sys.argv[2],
            "banda":sys.argv[3],
            "prioridade":sys.argv[4],
            "classe":sys.argv[5]
            }
        }

print(contrato)
print("\n")

tcp.sendall(json.dumps(contrato).encode())

#for i in range(0,100):
#    tcp.sendall(b"Aqui FUNCIONOU")

tcp.close()

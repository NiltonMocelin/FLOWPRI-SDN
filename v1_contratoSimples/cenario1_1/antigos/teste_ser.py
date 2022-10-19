import socket
import json

#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#tcp.bind(("10.123.123.1", 4444))
tcp.bind((socket.gethostbyname(socket.gethostname()),4444))

print("host:{0} Ouvindo em {1}".format(socket.gethostname(),socket.gethostbyname(socket.gethostname())))

tcp.listen(5)

while True:
    conn, addr = tcp.accept()
    print("Connectado: ")
    print(addr)
    print("\n")

    
    data = conn.recv(1024)
    contrato = json.loads(data)
    print(contrato)
    
    print(contrato['contrato'][0]['ip_origem'])

    print("contrato salvo \n")
#    contratos.append(contrato)




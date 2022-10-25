import socket

HOST="10.123.123.1"
#HOST="127.0.1.1"
PORT= 4444

#with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.connect((HOST, PORT))
    
for i in range(0,100):
    tcp.sendall(b"Aqui FUNCIONOU")

tcp.close()

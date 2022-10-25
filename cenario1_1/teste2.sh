#teste para verificar se as filas estao limitando no tamanho da banda do link = 10mb
python contrato_cli_v2.py 10.10.10.1 172.16.10.3 172.16.10.2 2000 1 1

#com cada host subir um iperf para verificar a banda obtida
# com o controlador tentar comunicar via best-effor um iperf e ver quanto de banda posso usar - nao deve ultrapassar os 10mb do link
[host h2]
iperf -s -p 80 &
iperf -s -p 90 &

[root1]
iperf -c -p 80

[host h3]
iperf -c -p 90

 -- resultado
[host h2]

Bandwidth
[root1-best-effort-sem meter] 7.38Mbits/sec
Bandwidth
[h3 - com meter] 2.09Mbits/sec



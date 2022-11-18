## Topologia
* domínio 1: root1-c1, s1
* domínio 2: root2-c2, s2
* domínio 3: root3-c3, s3
* domínio 4: root4-c4, s4
* domínio 5: root5-c5, s5

[root1-c1]      [root2-c2]     [root3-c3]       [root4-c4]     [root5-c5]
    |               |              |             |              |
    s1 ------------s2 ------------s3 ------------s4 ------------s5
    /                                                            \
 h1                                                               h4


# Para realizar as medições:
* Executar a topologia correspondente
`sudo python topo5_v2.py`

* Executar o script de configuração das filas (switchQueueConf2.sh)
`sh switchQueueConf2.sh`

* Um tcpdump na interface de h1
* Um tcpdump na interface de h4
* Um tcpdump na interface do controlador mais distante (último a processar)
* Executar os controladores semPrints e coletar os valores obtidos

`h1: python contrato_cli_v2.py 10.10.10.1 172.16.10.1 172.16.10.4 1000 2 2`
`root1-c1: ryu-manager c1_v2_semPrints.py --ofp-tcp-listen-port 7000`
`root2-c2: ryu-manager c2_v2_semPrints.py --ofp-tcp-listen-port 6699`
`root3-c3: ryu-manager c3_v2_semPrints.py --ofp-tcp-listen-port 6677`
`root4-c4: ryu-manager c4_v2_semPrints.py --ofp-tcp-listen-port 6688`
`root5-c5: ryu-manager c5_v2_semPrints.py --ofp-tcp-listen-port 6666`

`h1: ping -c 1 172.16.10.4`

* Espera expirar as regras dos switches

`h1: ping -c 1 172.16.10.4`


# Rodada 1:
* Tempo settar switches:
c1: 14
c2: 6
c3: 9
c4: 9
c5: 11

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 2


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT =  66


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 9

server-controlador (receber contrato de c1):
TT = 2

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 2

server-controlador (receber contrato de c1):
TT = 2

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1

server-controlador (receber contrato de c1):
TT = 4

* Tempo processamento c5:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

server-controlador (receber contrato de c1):
TT = 1


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TP = 68 + 26 = 94

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c5 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 3.224626
T2 = 3.284332 + 1/1000
TT = 3.284332 + 1/1000 - 3.224626 = 60.7

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 8.569585 - 8.569352 = 0.23


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 6

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 6

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 7


* Tempo processamento c5:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 2

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TT = 22

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 7.638820 - 7.598870 = 39.95

--------------------------------------------------------

# Rodada 2:
* Tempo settar switches:
c1: 4
c2: 7
c3: 7
c4: 7
c5: 6

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 2


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 49


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 4

server-controlador (receber contrato de c1):
TT = 3

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1

server-controlador (receber contrato de c1):
TT = 3

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 2

server-controlador (receber contrato de c1):
TT = 2

* Tempo processamento c5:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

server-controlador (receber contrato de c1):
TT = 2


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TP = 72

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c5 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 07:39:13.135520
T2 = 07:39:13.181171 + 2/1000
TT = 3.181171 + 2/1000 - 3.135520 = 47.65

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 0.372644 - 0.372466 = 0.18


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 0

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 0

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 9

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 2


* Tempo processamento c5:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 4

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TT = 15

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 1.660073 - 1.623349 = 36.72

--------------------------------------------------------

# Rodada 3:
* Tempo settar switches:
c1: 4
c2: 8
c3: 7
c4: 3
c5: 6

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 2


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 60


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 4

server-controlador (receber contrato de c1):
TT = 0

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 2

server-controlador (receber contrato de c1):
TT = 4

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1

server-controlador (receber contrato de c1):
TT = 0

* Tempo processamento c5:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2

server-controlador (receber contrato de c1):
TT = 1


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TP = 80

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c5 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 07:53:54.399255
T2 = 07:53:54.453808 + 1/1000
TT = 4.453808 + 1/1000 - 4.399255 = 55.55

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 3.034042 - 3.033863 = 0.18


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 3

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 2

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 5


* Tempo processamento c5:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 2

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TT = 13

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 7.262749 - 7.219892 = 42.85

--------------------------------------------------------

# Rodada 4:
* Tempo settar switches:
c1: 8
c2: 7
c3: 4
c4: 6
c5: 2

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 5


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 63


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 13

server-controlador (receber contrato de c1):
TT = 1

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 5

server-controlador (receber contrato de c1):
TT = 3

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 2

server-controlador (receber contrato de c1):
TT = 1

* Tempo processamento c5:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

server-controlador (receber contrato de c1):
TT = 1


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TP = 99

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c5 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 08:52:15.491710
T2 = 08:52:15.559058 + 1/1000
TT = 68.35

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT=  5.464753 - 5.464501 = 0.25


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 9

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 12

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 7


* Tempo processamento c5:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 4

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TT = 33

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT =  8.301218 - 8.241585 = 59.63

--------------------------------------------------------

# Rodada 5:
* Tempo settar switches:
c1: 12
c2: 10
c3: 4
c4: 8
c5: 10

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 4


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 14+1+15+6+1+14+6+3+5+13 = 78


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 3

server-controlador (receber contrato de c1):
TT = 2

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 2

server-controlador (receber contrato de c1):
TT = 2

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1

server-controlador (receber contrato de c1):
TT = 1

* Tempo processamento c5:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2

server-controlador (receber contrato de c1):
TT = 0


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TP = 98

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c5 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 08:58:54.895959
T2 = 08:58:54.960830
TT = 4.960830 - 4.895959 = 64.87

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 4.686424 - 4.686178 = 0.24


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 2

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 5

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 10

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 7


* Tempo processamento c5:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 3

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4 + tproc_c5
TT = 27

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 5.220700 - 5.154762 = 65.93

--------------------------------------------------------
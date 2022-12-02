## Topologia
* domínio 1: root1-c1, s1
* domínio 2: root2-c2, s2
* domínio 3: root3-c3, s3
* domínio 4: root4-c4, s4

[root1-c1]      [root2-c2]     [root3-c3]       [root4-c4]
    |               |              |             |
    s1 ------------s2 ------------s3 ------------s4
    /                                             \
 h1                                                h4


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

`h1: ping -c 1 172.16.10.4`

* Espera expirar as regras dos switches

`h1: ping -c 1 172.16.10.4`


# Rodada 1:
* Tempo settar switches:
c1: 8ms
c2: 5ms
c3: 7ms
c4: 8ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 2ms = 3ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 12ms + 1ms + 9ms + 3ms + 1ms + 11ms + 5ms + 1ms + 4ms + 3ms = 50ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 12ms

server-controlador (receber contrato de c1):
TT = 2ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms + 1ms = 2ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 2ms + 1ms = 3ms

server-controlador (receber contrato de c1):
TT = 3ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 54ms + 12ms + 2ms + 2ms + 3ms + 3ms + 1ms + 1ms = 78ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 2.689885
T2 = 2.749144 + 1/1000
TT = 2.749144 + 1/1000 - 2.689885 = 60.25

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 8.449137 - 8.448918 = 0.21ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 2ms + 2ms + 1ms = 6ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 1ms + 2ms + 1ms + 1ms + 3ms = 8ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms + 1ms + 1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 1ms + 6ms + 8ms + 3ms = 19ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 8.494684 - 8.445798 = 48.88

--------------------------------------------------------

# Rodada 2:
* Tempo settar switches:
c1: 13ms
c2: 13ms
c3: 11ms
c4: 6ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 2ms = 3ms


pkt_in_icmp16 (envia contrato para c2 e para c3 e c4): 
- TT = 10ms + 1ms + 5ms + 3ms + 7ms = 26ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 0ms

server-controlador (receber contrato de c1):
TT = 3ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 0ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 37ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 0.127256
T2 = 0.162560 + 1/1000 
TT = 0.162560 + 1/1000 - 0.127256 = 36.3

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 6.436296 - 6.435995 = 0.30ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 1ms = 2ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 1ms + 1ms + 2ms + 2ms = 6ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 3ms + 1ms = 4ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 13ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT =  1.957296 - 1.921826 = 35.46

--------------------------------------------------------

# Rodada 3:
* Tempo settar switches:
c1: 4ms
c2: 4ms
c3: 7ms
c4: 9ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 3ms = 4ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 10ms + 1ms + 11ms + 3ms+ 1ms + 9ms + 3ms + 7ms = 45ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 2ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 2ms

server-controlador (receber contrato de c1):
TT = 2ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 62ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 19:27:37.226221
T2 = 19:27:37.277953 + 1/1000
TT = 7.277953 + 1/1000 - 7.226221 = 52.73

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT=  2.946845 - 2.946584 = 0.26ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 5ms+ 1ms + 2ms = 9ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 1ms + 1ms + 1ms + 2ms + 2ms = 7ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms + 1ms + 1ms + 1ms = 4ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 1ms + 9ms + 7ms + 4ms = 21ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 5.616419 - 5.563490 = 52.92

--------------------------------------------------------

# Rodada 4:
* Tempo settar switches:
c1: 8ms
c2: 6ms
c3: 11ms
c4: 3ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 2ms = 3ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 10ms + 1ms + 13ms + 7ms + 1ms + 4ms + 20ms + 12ms = 68ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 3ms

server-controlador (receber contrato de c1):
TT = 2ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 7ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 2ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 89ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 8.539726
T2 = 8.592589 + 2/1000
TT = 8.592589 + 2/1000 - 8.539726 = 54.86

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 3.256457 - 3.256238 = 0.21


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms +1ms + 2ms + 1ms = 5ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 3ms + 1ms + 3ms = 7ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 2ms +1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 16ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 1.451599 - 1.416133 = 35.46

--------------------------------------------------------

# Rodada 5:
* Tempo settar switches:
c1: 8ms
c2: 6ms
c3: 3ms
c4: 5ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 3ms = 4ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 11 + 5 + 10 + 4 + 11 + 4 + 11 + 8 = 64ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 2ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 2ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 79ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 0.531233
T2 = 0.584676 + 1/1000
TT = 0.584676 + 1/1000 - 0.531233 = 54.44 

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 6.376751 - 6.376492 = 0.25ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 2ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 1ms + 2ms + 1ms = 5ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 1ms + 1ms + 1ms + 1ms + 3ms = 7ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 4ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 18ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 3.523618 - 3.473905 = 49.71

--------------------------------------------------------

# Rodada 6:
* Tempo settar switches:
c1: 9ms
c2: 13ms
c3: 13ms
c4: 6ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 3ms = 4ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 10ms + 1ms + 11ms + 5ms+ 1ms + 12ms + 5ms + 9ms = 54ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 5ms

server-controlador (receber contrato de c1):
TT = 0ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 3ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 71ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 0.728452
T2 = 0.782037 + 3/1000
TT = 0.782037 + 3/1000 - 0.728452 = 65.58

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 5.457183 - 5.456960 = 0.22ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 2ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 5ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 9ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 1.161117 - 1.137628 = 23.48

--------------------------------------------------------

# Rodada 7:
* Tempo settar switches:
c1: 7ms
c2: 7ms
c3: 7ms
c4: 4ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 4ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 11 + 20 +13 + 14 = 58ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 7ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 2ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 3ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 80ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 19:59:38.726246
T2 = 19:59:38.784027 + 3/1000
TT = 8.784027 + 3/1000 - 8.726246 = 60.78

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 3.771696 - 3.771439 = 0.25ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT =1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 5ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 6ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 4ms 

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 16ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 6.970913 - 6.922035 = 48.87

--------------------------------------------------------

# Rodada 8:
* Tempo settar switches:
c1: 10ms
c2: 15ms
c3: 19ms
c4: 7ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 4ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 57ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 5ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 6ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 3ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 81ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 4.229546
T2 = 4.275001 + 3/1000
TT = 4.275001 + 3/1000 - 4.229546 = 48.45

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT=  8.150812 - 8.150585 = 0.22ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 8ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 5ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 5ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 19ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 1.592677 - 1.545598 = 47.07

--------------------------------------------------------

# Rodada 9:
* Tempo settar switches:
c1: 4ms
c2: 3ms
c3: 3ms
c4: 8ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 2ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 29ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 2ms

server-controlador (receber contrato de c1):
TT = 3ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 42ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 6.927715
T2 = 6.964055 + 1/1000
TT = 6.964055 + 1/1000 - 6.927715 = 37.34

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 0.085333 - 0.085181 = 0.15ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 2ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 5ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 4ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 4ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 15ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 4.480937 - 4.441164 = 39.77

--------------------------------------------------------

# Rodada 10:
* Tempo settar switches:
c1: 7ms
c2: 2ms
c3: 3ms
c4: 6ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 5ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 62ms


* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 e c4 para encaminhar para c1):
TT= 2ms

server-controlador (receber contrato de c1):
TT = 2ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c4 para encaminhar para c1):
TT = 2ms

server-controlador (receber contrato de c1):
TT = 5ms

* Tempo processamento c4:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TP = 83ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c4 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 20:16:45.130796
T2 = 20:16:45.183666 + 1/1000
TT = 5.183666 + 1/1000 - 5.130796 = 53.86

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 5.189791 - 5.189082 = 0.7ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 6ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT = 8ms

* Tempo processamento c4:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 5ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3 + tproc_c4
TT = 20ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT =  2.456844 - 2.408053 = 48.79

--------------------------------------------------------

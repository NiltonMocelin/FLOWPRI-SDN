## Topologia
* domínio 1: root1-c1, s1
* domínio 2: root2-c2, s2
* domínio 3: root3-c3, s3

[root1-c1]      [root2-c2]     [root3-c3]
    |               |              |
    s1 ------------s2 ------------s3
    /                               \
 h1                                  h4



# Para realizar as medições:
* Executar a topologia correspondente
`sudo python topo5_v2.py`

* Executar o script de configuração das filas (switchQueueConf2.sh)
`sh switchQueueConf2.sh`

* Um tcpdump na interface de h1
* Um tcpdump na interface de h4
* Um tcpdump na interface do controlador mais distante (último a processar)
* Executar os controladores semPrints e coletar os valores obtidos

`h1: python contrato_cli_v2.py 10.10.10.1 172.16.10.1 172.16.10.4 1000 2 2
`root1-c1: ryu-manager c1_v2_semPrints.py --ofp-tcp-listen-port 7000
`root2-c2: ryu-manager c2_v2_semPrints.py --ofp-tcp-listen-port 6699
`root3-c3: ryu-manager c3_v2_semPrints.py --ofp-tcp-listen-port 6677

`h1: ping -c 1 172.16.10.4`

* Espera expirar as regras dos switches

`h1: ping -c 1 172.16.10.4`


# Rodada 1:
* Tempo settar switches:
c1: 6ms
c2: 6ms
c3: 6ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 36ms + 38ms = 74ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 6ms + 11ms + 4ms + 10ms = 30ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 3ms

server-controlador (receber contrato de c1):
TT = 2ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 74ms + 30ms + 1ms + 3ms + 2ms + 2ms + 1ms = 113ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 5.823645
T2 = 5.935843 + 1/1000
TT = 5.935843 + 1/1000 - 5.823645 = 113.19ms

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 0.457178 - 0.456952 = 0.22ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 2ms + 1ms + 2ms = 5ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 2ms + 1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 1ms + 5ms + 3ms =9ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 3.129321 - 3.105207 = 24.11

--------------------------------------------------------

# Rodada 2:
* Tempo settar switches:
c1: 4ms
c2: 7ms
c3: 7ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 2ms = 3ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 7ms + 1ms + 10ms + 3ms + 9ms = 30ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 4ms

server-controlador (receber contrato de c1):
TT = 2ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2ms

server-controlador (receber contrato de c1):
TT = 2ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 3ms + 30ms + 1ms + 4ms + 2ms + 2ms + 2ms = 46ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 13:41:25.322956
T2 = 13:41:25.363303 + 2/1000 
TT = 5.363303 + 2/1000 - 5.322956 = 42.34ms

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT=  9.890311 - 9.890131 = 0.18ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 1ms + 1ms = 3ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms + 1ms + 1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 1ms + 3ms + 3ms = 7ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 1.005159 - 0.980909 = 24.24ms

--------------------------------------------------------

# Rodada 3:
* Tempo settar switches:
c1: 10ms
c2: 13ms
c3: 3ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 1ms = 2ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 5ms + 1ms + 6ms + 4ms + 4ms + 1ms + 7ms = 28ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 1ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 2ms + 28ms + 1ms + 1ms + 1ms + 1ms + 1ms = 35ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 13:59:18.767477
T2 = 13:59:18.801729 + 1/1000
TT = 8.801729 + 1/1000 - 8.767477 = 35.25

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 4.949718 - 4.949526 = 0.19ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms 

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 1ms +1ms = 3ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 1ms + 3ms + 1ms = 5ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT =  7.859632 - 7.839105 = 20.52

--------------------------------------------------------

# Rodada 4:
* Tempo settar switches:
c1: 12ms
c2: 10ms
c3: 9ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 3ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 8ms + 4ms + 9ms = 21ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 0ms

server-controlador (receber contrato de c1):
TT = 3ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 29ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 6.423443
T2 = 6.454769 + 1/1000
TT = 6.454769 + 1/1000 - 6.423443 = 32.32ms

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT=  0.922157 - 0.921892 = 0.26ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 0ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 1ms + 2ms = 4ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 2ms + 1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 4ms + 3ms = 7ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 4.398428 - 4.380386 = 18.04

--------------------------------------------------------

# Rodada 5:
* Tempo settar switches:
c1: 8ms
c2: 5ms
c3: 5ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 1ms + 1ms + 10ms + 6ms = 18ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 0ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 1ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 0ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 1ms + 18ms + 1ms + 1ms + 1ms = 22ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 2.625315
T2 = 2.658718 + 1/1000
TT = 2.658718 + 1/1000 - 2.625315 = 34.40ms

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT=  5.434590 - 5.434393 = 0.19ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 3ms + 2ms = 6ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 3ms + 2ms = 5ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 1ms + 6ms + 5ms = 12ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 5.989353 - 5.963291 = 26.06

--------------------------------------------------------

# Rodada 6:
* Tempo settar switches:
c1: 7ms
c2: 6ms
c3: 6ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 1ms = 2ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 1ms + 4ms + 2ms + 4ms = 11ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 1ms

server-controlador (receber contrato de c1):
TT = 0ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 0ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 11ms + 1ms + 1ms + 1ms = 14ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 6.828264
T2 = 6.851976 + 1/1000
TT = 6.851976 + 1/1000 - 6.828264 =24.71ms

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 2.322775 - 2.322550 = 0.22ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 1ms + 1ms = 3ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms + 1ms + 1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 1ms + 3ms + 3ms = 7ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT =  6.885074 - 6.866987 = 18.08

--------------------------------------------------------

# Rodada 7:
* Tempo settar switches:
c1: 2ms
c2: 3ms
c3: 5ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 3ms = 4ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 7ms + 1ms + 9ms + 5ms + 10ms = 32ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 1ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 1ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 41ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 18:23:50.030003
T2 = 18:23:50.073896 + 1/1000
TT = 0.073896 + 1/1000 - 0.030003 = 44.89ms

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT=  3.701615 - 3.701370 = 0.24ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 2ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 1ms + 1ms = 3ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms + 1ms + 1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 2ms + 3ms + 3ms = 8ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT =  5.589609 - 5.566183 = 23.42

--------------------------------------------------------

# Rodada 8:
* Tempo settar switches:
c1: 4ms
c2: 4ms
c3: 7ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 4ms = 5ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 8ms + 1ms + 11ms + 5ms + 12ms = 37ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 3ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 2ms

server-controlador (receber contrato de c1):
TT = 2ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 5ms + 37ms + 1ms + 3ms + 1ms + 2ms + 2ms = 51ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 18:32:00.229294
T2 = 18:32:00.275290 + 2/1000 
TT = 0.275290 + 2/1000 - 0.229294 = 47.99ms

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT= 4.991709 - 4.991466 = 0.24ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 2ms + 1ms +2ms = 5ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms + 1ms + 1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 1ms + 5ms + 3ms = 9ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT =  7.744494 - 7.719941 = 24.55

--------------------------------------------------------

# Rodada 9:
* Tempo settar switches:
c1: 7ms
c2: 9ms
c3: 10ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 1ms + 6ms = 7ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 9ms + 1ms + 10ms + 2ms + 1ms + 7ms + 1ms + 1ms = 32ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 2ms

server-controlador (receber contrato de c1):
TT = 1ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 3ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 7ms + 32ms + 1ms + 2ms + 1ms + 1ms + 3ms = 47ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 
18:41:22.231899
T1 = 18:41:22.231899
T2 = 18:41:22.287980 + 3/1000
TT = 2.287980 + 3/1000 - 2.231899 = 59.08ms

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT=  7.649834 - 7.649685 = 0.14ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 1ms + 2ms + 1ms = 4ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms + 1ms + 1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 1ms + 4ms + 3ms = 8ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 4.053740 - 4.027329 = 26.41

--------------------------------------------------------


# Rodada 10:
* Tempo settar switches:
c1: 5ms
c2: 6ms
c3: 8ms

# Tempo para estabelecer um contrato entre h1-h4
* Tempo processamento c1:
server-host (receber contrato de h1+criar regras+icmp15):
- T1 = tempo consumido no tratamento do packet_in (para a volta da comunicacao controlador->host)
- T2 = tempo de processamento ouvindo a conexão e recebendo o contrato.
- TT = T1 + T2
- TT = 0ms + 3ms = 3ms


pkt_in_icmp16 (envia contrato para c2 e para c3): 
- TT = 6ms + 1ms + 11ms + 5ms + 2ms + 11ms = 36ms
 

* Tempo processamento c2:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

pkt_in_icmp16 (rec de c3 para encaminhar para c1):
TT= 2ms

server-controlador (receber contrato de c1):
TT = 2ms

* Tempo processamento c3:
pkt_in_icmp15 (receb icmp15 e respondido icmp16):
TT = 1ms

server-controlador (receber contrato de c1):
TT = 2ms


* Tempo Total de processamento:
(soma dos processamentos de c1, c2 e c3)
TP = tproc_c1 + tproc_c2 + tproc_c3
TP = 47ms

* Tempo total para setup de contratos:
T1 = primeiro pacote saindo de h1
T2 =  tempo que o primeiro pacote de c1 chega em c3 + processamento para receber o contrato e criar as regras (server-control)/ 1000 (milliseconds to seconds)
TT = T2 - T1 

T1 = 18:49:54.329490
T2 = 18:49:54.373210 + 2/1000 
TT = 4.373210 + 2/1000 - 4.329490 = 45.72ms

# Tempo para enviar um pacote icmp entre h1-h4 com regras ativas
* Não tem processamento, pois não ocorre packet_in
(tempo do icmp chegar em h4 - tempo do icmp sair de h1)
T1 = tempo do icmp sair de h1
T2 = tempo do icmp chegar em h4
TT = T2 - T1
TT=  6.213196 - 6.212968 = 0.22ms


# Tempo para enviar um pacote icmp entre h1-h4 sem regras ativas (packet_in)
* Tempo processamento c1:
T1 = packet_in: tempo consumido no tratamento do packet_in, encontrando match, criando regras e enviando icmp 15:
TT = 1ms

* Tempo processamento c2:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
T3 = pkt_in_icmp16:
TT (soma) = 2ms + 2ms + 1ms = 5ms

* Tempo processamento c3:
T1 = pkt_in_icmp15:
T2 = tempo consumido no tratamento do packet_in, encontrando match e criando regras:
TT = 1ms + 1ms + 1ms = 3ms

Tempo Total de processamento:
TT = tproc_c1 + tproc_c2 + tproc_c3
TT = 1ms + 5ms + 3ms = 9ms

* Tempo Total:
T1 = tempo quando o icmp sai de h1
T2 = tempo quando o icmp chega em h4
TT = T2 - T1
TT = 7.287280 - 7.261968 = 25.31

--------------------------------------------------------
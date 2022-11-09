# TESTES DE FUNCIONALIDADE/ESCALABILIDADE DO FRAMEWORK

- controlador base : 2c_1r_1sc/c1_v2_semPrints.py

* Foram desenvolvidos varios cenarios nomeados conforme a quantidade de controladores e switches (1c = 1 controlador, 1sc = 1 switch em cada dominio/para cada controlador gerenciar)
* Foram desenvolvidos mecanismos de enderecamentos para suportar o ambiente de rede mininet, onde os controladores compartilham a mesma tabela de route e de arp, de modo que os controladores se comuniquem por dentro da rede mininet, como se fossem hosts (assim como definindo na proposta inicial).
* Para entender o enderecamento proposto, importar a configuracaoEndFict.drawio em https://app.diagrams.net/
* As mensagens OpenFlow entre controladores e switches continuam ocorrendo de forma direta, sem passar pela rede mininet.

## Medida de tempo de execução:
* A passagem de tempo pelo Framework pode ser percebida de duas formas: tempo de processamento e tempo de comunicação. O tempo de processamento é o tempo do processamento do Framework propriamente dito, já o tempo de comunicação envolve a velocidade da interface de rede e dos mecanismos do protocolo OpenFlow juntamente com ovs e seus similares.

* O Tempo de processamento total é obtido pelo somatório do tempo dos seguintes processos:

i) Tempo de processamento de settar um switch (switch_features)



ii) Tempo de processamento do server-hosts (servidor ouvindo hosts)
|- 1: Tempo inicial - conexão aceita
|- 2: Tempo decorrido por AlocarGBAM
|- 3: Tempo decorrido para criar as regras nas classes switch no controlador e nos switches OVS (sem contar o tempo de ativação das regras nos switches ovs)
|- 4: Tempo para enviar o ICMP 15 (sem contar o tempo de recebimento)
|- 5: Tempo final - conexão fechada

iii) Tempo de processamento do server-controladores (servidor ouvindo controladores)
|- 1: Tempo inicial - conexão aceita
|- 2: Tempo decorrido por AlocarGBAM
|- 3: Tempo decorrido para criar as regras nas classes switch no controlador e nos switches OVS
|- 4: Tempo final - conexão fechada

iv) Tempo de processamento Packet_In ICMP 15 (recebido)
|- 1: Tempo inicial - packet_in
|- 2: Tempo de enviar o icmp 16
|- 3: tempo de criar as regras de recebimento do futuro contrato - alocarGBAM.
|- 4: tempo de envio da sequencia do icmp 15

v) Tempo de processamento Packet_In ICMP 16 (recebido)
|- 1: Tempo inicial - packet_in
-- Controlador é o destino
|- 2: Tempo de procurar o contrato desejado 
|- 3: Tempo de criar regras para enviar o contrato
|- 4: Tempo de enviar o contrato
-- Controlador não é o destino
|- 2: Tempo de criar as regras em todos os switches da rota, para os contratos atravessarem o domínio
|- 3: Tempo de dar sequencia no icmp 16


vi) Tempo de processamento Packet_In com match nos contratos
|- 1: Tempo de encontrar o match
|- 2: Tempo de enviar o icmp 15
|- 3: Tempo de criar as regras nos switches/classe switch no controlador
|- 4: Tempo de injetar o pacote

vii) Tempo de processamento Packet_In sem match nos contratos
|- 1: Tempo de criar as regras nos switches
|- 2: Tempo de injetar o pacote

* Tempo de comunicacao = tempo levado por um pacote para atravessar um switch
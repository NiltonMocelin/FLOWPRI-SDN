--- syslog
# TESTE ::: tempos -> host1 criar contrato para comunicar com host4

* Tempo de processamento e comunicacao em um cenário onde dois domínios de rede 
compativeis com o framework estão conectados por um roteador/domínio, que não possui suporte ao framework (best-effort).

## Topologia
* domínio 1: root1-c1, s1
* domínio 2: roteador
* domínio 3: root2-c2, s2

[root1-c1]                  [root2-c2]
    |                          |
    s1 -----  roteador -------s2
    /                          \
   h1                           h4


* O roteador simula a ideia de componentes de rede que nao suportam o framework

 * Em cada teste fechar os controladores e remover as regras das tabelas de fluxo dos switches:

` ovs-ofctl del-flows s1`
` ovs-ofctl del-flows s2`
`h1: python contrato_cli_v2.py 10.10.10.1 172.16.10.1 172.16.10.2 1000 1 >> tempo1.saida`
`root1-c1: ryu-manager c1_v2_semPrints.py --ofp-tcp-listen-port 7000 >> tempo1.saida`
`root2-c2: ryu-manager c2_v2_semPrints.py --ofp-tcp-listen-port 6699 >> tempo1.saida`


* Tempo é obtido em 7 estados:


- t0: tempo envio primeiro pacote para estabelecer conexão


- t1: pkt bateu no controlador e o controlador respondeu, no entando o pkt de resposta resultou em pkt in:


- t2: regras criadas- reinjetando o pkt:


- t3: pkt reinjetado-saiu do pkt in


- t4: conexao iniciada - para receber o contrato


- t5: enviando icmp - 15


- t6: icmp 15 enviado - fim do recebmento dos contratos

- Apartir de t6 o host pode enviar pacotes com a banda definida

--->>> teste com vlc
- situacoes de prioridade > banda > mudar


# TESTE 2 - roteador gargalo/congestionado:

* verificar o impacto que um roteador congestinoado implica nos requisitos de QoS de um fluxo.
* Um host envia o contrato com os requisitos de um fluxo que é alocado em dois domínios, mas 
entre eles existe um roteador congestionado e o fluxo não terá seus requisitos garantidos ( conforme topologia apresentada em cima).



# TESTE 3 - tempo sem framework

# TESTE 4 - escalabilidade aumentar controladores/switches


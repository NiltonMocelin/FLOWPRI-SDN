# TESTES DE FUNCIONALIDADE/ESCALABILIDADE DO FRAMEWORK

* Foram desenvolvidos varios cenarios nomeados conforme a quantidade de controladores e switches (1c = 1 controlador, 1sc = 1 switch em cada dominio/para cada controlador gerenciar)
* Foram desenvolvidos mecanismos de enderecamentos para suportar o ambiente de rede mininet, onde os controladores compartilham a mesma tabela de route e de arp, de modo que os controladores se comuniquem por dentro da rede mininet, como se fossem hosts (assim como definindo na proposta inicial).
* Para entender o enderecamento proposto, importar a configuracaoEndFict.drawio em https://app.diagrams.net/
* As mensagens OpenFlow entre controladores e switches continuam ocorrendo de forma direta, sem passar pela rede mininet.


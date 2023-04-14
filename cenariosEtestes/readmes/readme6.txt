

#############################################################################
#22/06/22
1- Criar um codigo para cada controlador
2- Criar tabelas de roteamento nas instancias dos switches de forma estatica
3- Ajustar o TOS, para que a maneira com que se lida no codigo do controlador seja a mesma que o ovs faz.
4- No pacote ICMP, incluir o IP de HOST destino nos dados do pacote no ICMP reply. Para que o controlador que for tratar o reply possa identificar quais contratos devem ser enviados. Testando linha +-985
5-OBS -- Implementar : garantir que exista apenas um contrato com match para ip_src, ip_dst - e mais campos se forem usar - que se 
outro contrato vier com esse match, substituir o que ja existe.
5- Mudar a topo4.py para incluir as informacoes de roteamento (route e arp) e simplificar alguns processos que nao sao importantes nessa etapa. (testando em topo5.py)
6- Testar as marcacoes de FLAG e os eventos
7- Testar a descoberta de controladores (ICMP) e a troca de contratos.


OBS: o ICMP request information é bem útil, ele anuncia para os controladores na rota entre origem e destino, que um fluxo irá trafegar, como se perguntando quem quer colaborar com o fornecimento de recursos corretos.
No entanto, utilizar o ICMP reply information pode ser um problema, pois envia o ip do host destino nos dados da mensagem. Esse IP eh necessario pois quando um controlador recebe um ICMP information reply, o ip origem é de outro controlador e o ip destino é deste controlador em questão, não sendo possível identificar qual é o host destino, ou seja, quais contratos devem ser enviados para o controlador que respondeu. No entanto, o controlador que respondeu sabe quem é o host destino pois o request tinha esse ip como destino, por isso, se este ip destino for acrescentado como DATA no reply, o controlador que recebe um reply sabe quais contratos devem ser enviados.

Assim, caso isso se torne um problema que demore a ser resolvido, deve-se esquecer a abordagem do information reply por não ter como saber quais contratos sao desejados, e criar um novo socket, por onde os controladores que receberem icmp information request devem solicitar os contratos. <---- muito mais simples >> A se considerar....
	

#---antigo ---------- (feito ate 7)
#Topicos a implementar no controlador:

1- o controlador deve identificar quando o pacote que chega for um pacote ICMP request information. Para isso, precisa de regras especificas na tabela 0, encaminhar todo o 

2- o controlador deve responder o request information e tbm mandar um request na direcao que o antigo estava tomando, pois o pacote deve alcancar outros controladores tbm.

3- Decidir se o send do request information sera no socket ao receber o contrato ou no packet-in - me parece mais correto na funcao do socket.

4- criar classes para os switches armazenarem as informacoes de suas filas e regras. - as informacoes dos switches e dos contratos -  poderiam ser atualizadas sempre que ocorrer um novo contrato.
#criar as classes de switches
#criar os vetores necessarios
Quando um switch conecta com o controlador - a classe deve ser instanciada



5- criar a logica de gerenciamento/compartilhamento de largura de banda utilizando as classes dos switches.

6- criar as filas nas portas dos switches

7- teste e experimentos

8- testar com um controlador com o framework em cada borda e um controlador sem o framework no meio -> preciso ver o quanto um gargalo nessa rede afeta a minha abordagem. --- provavelmente terei de assumir que o caminho todo utiliza o framework.

9- arrumar para obter a informacao de porta de saida pelo ip da rede. Por agora soh se obtem pelo endereco mac, que deve ser usado apenas para a vizinhanca do switch.

10- possivelmente terei que implementar BGP e terei que mudar varias coisas no codigo para adaptar.

##################################################@@##########################

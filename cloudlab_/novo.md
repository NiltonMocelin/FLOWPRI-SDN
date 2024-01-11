
# Informações:

* FLOWPRI_SDN docker versão de 10/01/2024

## Objetivos finais do FLOWPRI:

* Deve funcionar no core: manter o desempenho e o QoS per-fluxo agregando fluxos. com regras meter. 

* Não deve ter problemas com NAT

* Deve garantir QoS fim-a-fim

* Deve fornecer estatísticas dos fluxos/QoS

* Deve fornecer estatísticas dos switches 

* Deve fornecer informações para definir estratégias de gerenciamento - como deploy de switches e roteamento.

* Deve ser vantajoso para ISPs - QoS as a Service

## Objetivos parciais de implemmentacao:

* Refatorar o flowpri pq esta uma bagunca do caramba

* Interface WEB {

	- Ver a topologia

	- Ver estatísticas dos switches e da rede

	- Ver recursos disponíveis

}

* Nao precisa utilizar multithreading{
	
	- Sobe um socket.

	- Quando uma conexão é estabelecida, os div são atualizados com os dados
recebidos e a pagina deve ser renderizada novamente.
	
}


### Fazer agora

* Implementar no FLOWPRI um socket para recuperar informacoes do controlador utilizando json -- tipo porta 9999

* Substituir o DSCP por um classificador ML

### Como evitar ARPs -> definindo default gateway

* Sempre que o pacote for para um host na mesma rede, o próprio host emissor deve enviar um ARP

* Sempre que o pacote for para um host de uma rede diferente, o host emissor deve envia-lo ao defalt gateway (com ip e mac já conhecidos).

* aa

# Algumas direções para serem implementadas/exploradas

-> olhadinha nas mensagens Experimenter -- principalmente para implementar filas...

-> modificar a maneira de gerar as rotas {
	-> ver qual switch conhece o end MAC de origem (o switch que ja gerou um packet in desse host e armazenou) e apartir desse switch obter os outros que compoe a rota.  
	-> usar tbm a mascara de rede para descobrir qual prefixo utilizar ? ou isso eh uma coisa já sabida pelo  controlador? --> tudo /24 a principio
}


-> encontrei um trabalho com codigo para comparar - amirashoori7


-> poderia verificar se as portas dos switches existem com switchportstate message [openflow] -> se retornar algum erro ou informacao estranha alterar a configuracao da porta - tipo verificar as portas ativas e tal...

-> Modificar as configurações de rotas
-> Mudar como se obtem as rotas e os switches das rotas
-> Mudar como se aprende o endeço MAC para que cada switch saiba quais endereços mac são do seu domínio
-> implementar contratos com portas
-> implementar suporte a ipv6
-> implementar suporte a NAT -> mas ainda não sei como fazer isso - não entendi muito bem

--> tendo isso feito -> fazer os testes de fato

-> colocar o codigo do github no lattes -> software sem registro
-> trabalhos publicados em anais de eventos ( AINA )

Que tipos de testes:
	- teste onde um switch intermediario não utiliza flowpri
	- teste onde um switch intermediario está sem largura de banda suficiente e rejeita o contrato
	- teste com multiplos fluxos onde todos os switches utilizam flowpri e possuem banda suficiente
	- teste com multiplos fluxos onde todos os switches utilizam flowpri e um não possui banda suficiente
	- teste com multiplos fluxos onde um switch não utiliza flowpri e possuem banda suficiente

#09/05
-> Configurar o servidor/tratador de configuracoes para receber os dados dos switches e armazenar no controlador

-> fazer testes

#03/05

-> configurando melhor como o controlador recebe as configuracoes dos switches
-> falta melhorar e abrir uma porta para receber arquivos de configuracao
-> talvez devesse ter utilizado rest mesmo ... talvez estudar e criar uma versao rest
-> no fim, a parte grafica tera de ser web se for implementada (para ver o grafo da rede e tals)
-> arrumar mais algumas coisas para facilitar o uso por outros
-> fazer testes

#26/04
-> Arrumar a parte das configurações dos switches e aprendizagem mac.
-> NAO ESTAMOS ATUALIZANDO TODAS AS PORTAS COM A CONFIGURAÇÃO DA RESERVA DE LARGURA DE BANDA!!{
	- quando um fluxo reserva largura de banda, apenas a porta de saída dos switches são atualizados com a largura de banda utilizada, falta 
	fazer isso na porta de entrada tbm, pois essa porta não poderá utilizar largura de banda (é isso certo?)
}

-> utilizar mensagem openflow para configurar as filas nos switches!

-> [problema] como descubrir se um fluxo está recebendo os recursos -> um processo nos hosts clientes que responde um icmp 15 sobre o qos recebido em um fluxo para o controlador que o enviou.
-> [problema] NAT traduz endereços de origem e destino algumas vezes, como enviar um contrato de qos para outros dominios sendo que os ips podem ter mudado 
em domínios intermediários que nem suportam o flowpri-sdn. -> o contrato evita que multiplos domínios tenham que descobrir os requisitos do mesmo fluxo.




#18/04

-> configurar nos hosts e nos root-hosts, em suas tabelas de roteamento, rotas para default gateway. O default gateway é para onde pacotes fora da rede local são enviados. ASSIM, SE EVITAM OS ARP PACKAGES DOS HOSTS

-> Mudar os endereços IP dos hosts para estarem em redes diferentes.
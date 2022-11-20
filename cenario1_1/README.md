##############################################################################################################

# Estado atual

* Versão mais atual v2_testeComSem/testeDrop/5c_1sc_modificado/c1_v2.py -- suporta 5 controladores (criei traduções de enderecos para 5 controladores)
* V2: versão final 2.



* verificar onde colocar os prints de tempo e fazer os testes.
* hoje: vazer os gráficos e comecar o artigo.

* Versão: v2 - foi refeita a funcao getRotas e a switch_features ficou mais generica, para habilitar os testes com multiplos controladores
* c3_1sc - framework funcionando para 3 controladores. Infelizmente, é preciso configurar no código (não deu tempo de fazer por arquivo por exemplo).
* c4_1sc - configurado - testar e obter os valores de tempo

* pelo que vi, c3 e c4_1sc estão criando as regras de forma correta - mas por vezes, não cria rápido o suficiente e os pacotes geram packet_in, mesmo com as regras já tendo a criação ordenadas. Nesse caso, são criadas regras best-effort e o pacote é injetado. O "segundo" pacote, vai ser encaminhado pela regra correta e a best-effort vai expirar.

- [Funcionando+testado] Para 3 controladores e 1 switch cada 
- [Nao-testado] Para 3 controladores e multiplos switches (teria que colocar as configuracoes de rotas nos switches)

* único problema que torna meio irreal é: durante o estabelecimento do contrato já queremos criar as regras, mas nesse momento não sabemos qual o switch que recebeu o contrato primeiro. Assim, não teria como pegar as rotas baseado no switch de packet_in, conforme pensado a principio. Então é colocado em um vetor, qual seria o switch que inicia a rota para um host. Poderia ser por prefixo tbm - enfim, rotas não é o escopo do trabalho, assumimos que é sempre possível obter os switches que pertencem a uma rota entre host origem e destino.

* OBS: dump-flows é melhor com --stats junto:
`ovs-ofctl -O OpenFlow13 --stats dump-flows s1`


****** [FEITO] OBSS >>> ALTERAR TODOS OS switchQueueConf.sh -> atual: a taxa limite para cada fila é igual a minima - nesse caso, fluxos best-effort são limitados a banda reservada para best-effort -> alterar: classe best-effort "other-configs:max-rate:$BANDA". Isso permite que o HTB distribua banda excedente para essa classe. Infelizmente, não adianta distribuir a banda best-effort ou de outras classes para classes prioritarias, pq não tem como saber quanto de banda os fluxos best-effort usam e então não é possível garantir que os recursos emprestados sejam reservados para os fluxos prioritários.



### TODO:
* [Fazendo] (TOPOLOGIA) fazer as topologias de cada teste
|-> criados os switches e controladores
|-> falta configurar as rotas/arps e ips ficticios (desenvolvendo em draw.io)

* [FAZER] (CÓDIGO) arrumar as partes não genéricas e criar as rotas e configuracoes para cada teste

--------------------------------------------------------
### OUTROS:

- fazer os testes de tempo do impacto da quantidade de controladores para verificar se é possível criar uma regressão.
- verificar como o tempo escala com o aumento da quantidade de switches

- fazer os testes de quanto tempo leva para um pacote ser processado num switch controlador pelo framework vs um sem o framework
- o tempo de overhead de um cenário sem framework é zero, então a comparação deve ser feita quanto ao tempo de processamento no switch.

- comparar cenário com sobrecarga - com e sem framework

- mostrar que funciona

- apresentar o algoritmo - sequencia de passos

- mostrar que um fluxo de maior prioridade tem menos perda de pacotes usando o framework que sem, pois pode definir seus requisitos.

- e com isso acaba artigo e tcc -> so escrever

- se sobrar tempo, pensar na tela como subprocesso lendo dados por arquivos...



* criar uma tela ? (tenho um modelo pronto com python tkinter, só adaptar -> uma tela para mostrar os logs de packet_in's e botoes para mostrar as regras dos switches do domínio/slice) -pelo que vi, nao tem biblioteca gui que possa ser inicializada em uma thread diferente da principal em python. Duas alternativas, o controlador salva os estados dos switches e os logs em arquivos e um outro processo tela, le esses arquivos para mostrar. Outra alternativa é aprender a usar a biblioteca ReadProcessMemory, para ler a memoria do controlador e pegar o vetor de switches para obter as regras, mas seria um problema obter os logs, que poderiam ser gravados em um arquivo...- a tela seria outro processo tbm. -- parece que em python as aplicacoes precisam ser planejadas para rodar sobre telas e nao deixar elas por último.. ---- o melhor eh usar a primeira abordagem, salvar os logs e estado dos switches em arquivos - cada vez que adiciona/deleta uma regra, reescrever

* revisar partes do framework para deixar mais genérico: em algumas partes foquei na configuracao para o switch quando for de borda e conectado ao controlador... (acho que só no switch_features, mas melhor rever)

* foi modificado o recebimento de contratos dos clientes no controlador em v2_testeComSem e foi esquecido de puxar para o principal, nao muda nada mas eh bom arrumar

* modificar: se recebe um contrato que eh igual ao que ja tem, nao fazer nada... - agora esta removendo o igual, removendo as regras, adicionando novas regras ... nd ver

* escrever os textos (tcc e artigo)

* foram pesquisados novos trabalhos relacionados: encontrei alguns melhores, mais recentes e mais próximos do meu.

* alterar este arquivo -> melhorar o markdown + todos os problemas e solucoes -> adicionar o pq o problema surgiu e não apenas descição + como foi solucionado

## Versões
* c1_v1: o basico esta implementado (alocarGBAM, troca de contratos, estabelcer contratos, criacao de regras ...), porém, a comunicacao entre controladores ocorre fora do mininer.
* c1_v2: modificado a forma de comunicacao entre controladores, agora ocorre dentro do mininet + os contratos so sao trocados caso o solicitante tenha um contrato com tos diferente

# Como executar/comandos úteis:

* Rodar a topologia:

` sudo python topo5_v1.py`

* Rodar o script que cria as filas nas portas dos switches:

` sudo sh switchQueueConf2.sh `

* Abrir os roots 1 e 2, e rodar os controladores:

` xterm root1 root2`

* no root1:

` ryu-manager c1_v2.py --ofp-tcp-listen-port 7000`

* no root2:

` ryu-manager c2_v2.py --ofp-tcp-listen-port 6699`

* para um host criar um contrato (ex. host1->host4: ipcontrolador, ip_src, ip_dst, banda: 1000kbps, prioridade: 1, classe: 2):

` python contrato_cli_v2.py 10.10.10.1 172.16.10.1 172.16.10.4 1000 1 2`

## Comandos úteis:

* sempre rodar mininet clear antes de um teste:
`sudo mn -c`

* mostrar as regras meters, meter bands e status:
`ovs-ofctl -O OpenFlow13 meter-features s1`
`ovs-ofctl -O OpenFlow13 dump-meters s1`
`ovs-ofctl -O OpenFlow13 meter-stats s1`

* monitorar alteracoes nas tabelas de fluxo dos switches (com --stats mostra mais informações):

` watch ovs-ofctl dump-flows s1`

`watch ovs-ofctl -O OpenFlow13 --stats dump-flows s1`

* deletar todas as regras de fluxo de um switch:

` ovs-ofctl del-flows s1`

* listar filas em uma porta de um switch:

` sudo ovs-ofctl list qos`

` sudo ovs-ofctl queue-stats s1`

` sudo ovs-appctl qos/show s1-eth1`

* listar configuracao qdisc de uma interface:

` tc qdisc show`

` tc class show dev s1-eth1`

* listar meters instaladas em um switch:

` ovs-ofctl dump-meters s1`

* ouvir uma interface:

` tcpdump -i s1-eth1`

* verificar tabela route de um host ( controladores compartilham da mesma tabela ):

`route -n`

* verificar tabela arp:

`arp -n`

* deletar filas usando ovs:

` ovs-vsctl clear port s1-eth1 qos`

ou

` ovs-vsctl --all destroy qos `

* deletar filas usando tc:

` sudo tc qdisc del dev s1-eth1 root`

* Em caso de algum comando retornar algo como:

- "ovs-ofctl dump-meter s1 ovs-ofctl: none of the usable flow formats (OXM-OpenFlow13,OXM-OpenFlow14,OXM-OpenFlow15) is among the allowed flow formats (OpenFlow10,NXM)"

- Usar -O OpenFlow junto com o comando (ex.)  ovs-ofctl -O OpenFlow13 dump-meters s1

* em caso de ter problema com tinyrpc -> 
 ` sudo pip uninstall tinyrpc`
 ` sudo pip install tinyrpc==0.8`


##############################################################################################################
# UPDATES: IMPLEMENTACAO
##############################################################################################################
OBS: as acoes no vetor actions de uma mensagem de modificacao OpenFlow, ocorrem em ordem posicional do vetor - cuidado com a ordem das acoes

-------------------------
*** Controlador dominio 1 - - - c1_44.txt
- revisar o código [ok]
- revisar os diagramas do algoritmo e definir alterações

- verificar se as regras da tabela de encaminhamento estao sendo criadas corretamente.
|- na conexão com os switches


Tabela de Marcação/Classificação:
#1 regras de marcação + enviar para tabela de encaminhamento (2) - criadas quando um fluxo é aceito (pacotes com match em contratos) 
#2 regra encaminhar para a tabela (2)

Tabela de Encaminhamento:
#1 regras criadas para enviar pacotes com banda e filas específicas.
#2 regra para encaminhar para o controlador
#3 regra para pacotes ICMP 15 ser encaminhado ao controlador, desde que ip_src != ip_controlador #nao sera assim, pois no caso onde o ICMP inf. req. está no segundo domínio por ex., o end. origem != ip_controlador e seria encaminhada por cada switch para o controlador. -> para resolver isso, o pacote é analisado apenas no primeiro controlador e injetado no último switch da rota -- eu preferia uma forma aplicável na vida real e não essa "mágica"
#4 regra para pacotes ICMP transitarem pelo canal de controle #as regras devem ser injetadas para serem postas na fila de controle.
#5 regra para pacotes com destino o controlador, transitarem pelo canal de controle

OBS: no entanto, no segundo domínio, cada switch vai encaminhar ao controlador, por isso,
é preciso tratar essa situação. Uma solução é, o primeiro switch vai enviar o pacote ao
controlador, e este responde com inf. reply por meio do switch que disparou o packet in. 
Deste modo, o pacote inf. request vai ser reinjetado no último switch da borda próxima
do destino, para que os switches do "meio" não precisem tratar este pacote. 
Desta forma --> (recebe o inf. req.) s1 .... s4 (injetado o inf. req.)

* sobre a prioridade (obs: sempre que um fluxo for direcionado para uma fila inexistente, ele é encaminhado para o padrao id0):
- PARA o HTB: Menor valor é maior prioridade.
- Para o framework (senso humano): Maior valor maior prioridade.
- Ordem das filas e suas prioridades: 
-- classe1 (tempo-real) -> id(prioridade) -> [q0(p10), q1(p5), q2(p2)]
-- classe2 (dados) -> id(prioridade) -> [q3(p10), q4(p5), q5(p2)]
-- classe3 (best-effort) -> id(prioridade) -> [q6(p10)]
-- classe4 (controle) -> id(prioridade) -> [q7(p2)]


#### Solução para multiplos encaminhamentos em ICMP 15/16 ---> escolher um switch como sendo 
o "especial" para tratar esses tipos de solicitações, assim, garanto que apenas um faz o encaminhamento.


****** {SSH nos hosts
****** [mininet] Aparentemente, os hosts fazem parte do mesmo processo e assim não podem rodar cada um uma aplicação firefox por exemplo.
****** [mininet] no entanto, aparentemente se os hosts forem criados no espaço fora do ambiente mininet ( da mesma forma que o host root do controlador ), cada host vira um processo e assim podem cada um executar, por exemplo, um sshd.
****** [mininet] NAAH errei, o que está escrito acima está errado - posso subir um sshd em cada host mesmo no ambiente mininet: "/usr/sbin/sshd -D &"
****** [funcionou] AGR FUNCIONOU -- settar PermitRootLogin yes em /etc/sshd/sshd_config e definir a senha do root sudo passwd root, entao pode dar ssh ip
****** }

************** [ir colhendo as contribuicoes]:
------


################################################################################################################
######################################## ERROS/SOLUCOES/TODO ###################################################


************* ARRUMAR ICMP/contratos - configurar o envio dos contratos para o controlador que responder
- #enviar_contratos(host_ip, host_port, ip_dst_contrato)
  # - host_ip e host_port (controlador que envia)
  # - ip_dst_contrato #ip do host destino (deve estar nos dados do pacote icmp 16 recebido
  #pegar os dados do pacote
  #montar o json
  #filtrar o ip_dst
  #colocar em enviar contrato

************* [foi amenizado com identificacao no packet_in se for comunicacao com controlador vai criar regra para fila de controle] Quando o root que quer enviar uma mensagem - por exemplo trocar contratos ou estabelecer uma conexao tcp é preciso já criar as regras com o controlador, caso contrario é gerado um packet_in e entao é gerado as regras:
- Na verdade acho que não há o que fazer, só se fosse possível prever a conexão de um host com o controlador ou se o tcp esperasse a criação das regras antes de aceitar a conexão
- no entano é uma regra provisória que vai receber no máximo pacotes de handshake do lado root->host e então vai sumir devido ao idle_time 
- aparentemente no mesmo momento que se aceita uma conexao ocorre o evento packet_in - melhor printar o tempo para ver se dentro do recebimento da conexao nao se pode ja criar as  regras , mas parece nao ter jeito
- pq so depois de criar as regras que a conexao é aceita e o contrato é recebido.
- nao tem importancia acho

{
	- implementar o novo alocarGBAM [ok]
	- testar as filas, como se comportam cheias - com toda a banda alocada [parece-tudoOK]
	- testar a parte de emprestar banda [ok]
	- comparar um cenario com o framework e um sem:
		- questao de tempo para o primeiro pacote chegar no destino
		- tempo entre o primeiro pacote e o segundo
		- perda de pacotes quando uma aplicacao usa toda a banda e um novo fluxo prioritario necessita trafegar
		- efeito que um switch best-effort causa, efeito que varios switches best-effort causam
		- tempo de comunicacao entre controladores
		- banda utilizada pela comunicacao entre controladores para o estabelecimento de um contrato e multiplos contratos
		- efeito da priorizacao - comparar se uma fila com maior prioridade entrega com menor atraso que uma fila com menor prioridade.
	- ver do novo mecanismo de emprestimo, mudar os campos tos para que as duas classes tenham tos equivalentes [ok]
}



************** ARRUMAR melhorar o contrato - inserir protoco: tcp ou udp, e porta destino:
- adaptar o codigo
-- que vai ter varios contratos por host, cada um valido para uma aplicacao/porta

************* [ARRUMAR] USANDO PCAP::
- analisar o que está acontecendo nos hosts destino e origem

************ ARRUMAR - criar mecanismo para remover contrato - um host pode querer que um fluxo passe a trafegar como best effort

************** ARRUMAR - envio de contratos e expiraçao de contratos:
 x- [rejeitado] quando a regra de marcacao expira, remover o contrato? [NAO - ideia rejeitada]
 x- [rejeitado] modificar a remocao do controlador com timestamp, marcar os contratos e definir uma thread para observar os timestamps e remover [NAO - ideia melhorada]
-> [envio de contratos] no momento, sempre que ocorre um packet in, o contrato eh oferecido, os controladores respondem icmp 16 para receber o novo contrato, independente se ja possuem o mais atualizado
[solucao] - modificar para que enviem o tos e as informacoes necessarias para identificar um contrato, como (ip e porta), ou no icmp 15 ou no 16, para que seja possivel identificar se eh necessario enviar/solicitar o contrato, ou se ja tem o mais atualizado

-> [expiracao] no momento, os contratos sao permanentes:
[solucao] - criar um timestamp que sempre que ocorrer um packet in, os contratos que passaram o timestamp sejam removidos.

*************** ARRUMAR - só aceitar contratos de controladores que ja enviaram icmps 15 para o dominio:
- salvar os enderecos ip dos controladores conhecidos e outro vetor com os enderecos ip dos controladores que enviaram icmps.
- quando receber o contrato, remove do vetor o controlador que enviou
- eh um tratamento fraco de seguranca

   ################################################################################################################
######################################  FEITO/ARRUMADO/RESOLVIDO #####################################################


************ [RESOLVIDO] - contrato sendo ignorado [NAO ERA ERRO] :  por algum motivo o contrato estabelecido com h1-c1 5000 1 1 não está sendo distribuido, verificar o pq - se for 1000 1 1 funciona... (só precisa funcionar o 5000 para o teste de drop) 
--- SOLUCAO: Na verdade a banda total é 10Mb, mas dividido para a classe que sobra 3.5Mb para classe 1 e 3.3Mb para classe 2, logo elas podem emprestar banda mas não podem "quebrar banda" nessa versão, não pode ter 2Mb em uma classe e 1Mb em outra... Por isso, o fluxo é descartado e o contrato não é enviado :) -- aumentar a banda do link para "caber" o fluxo resolveria a situação.



************ [ARRUMADO] - ICMP inf. req. (15) :
- colocar nos dados o ip_src, que junto com o destino do pacote, formam o par origem e destino do contrato anunciado
- assim, controladores ao longo da rota podem analisar se desejam o contrato e ainda solicitar exatamente o contrato referente ao ip_src, ip_dst, informando no campo de dados
- pq, o controlador que responde com icmp inf. reply informa o ip_dst, assim, sao enviados todos os contratos referentes. No entanto, para cada novo fluxo
eh gerado um novo icmp inf. req. que vai exigir o recebimento de um novo contrato, mesmo que tenha acabado de receber o contrato junto em um processo de troca de contratos anterior


************** [FEITO] - no momento de enviar os contratos para um controlador que solicitou com icmp 16, as regras criadas nao sobem ou podem nao subir a tempo de se enviar os pacotes do contrato e vao gerar um packet_in:
- neste caso, se um packet in ocorrer, vai ser um pacote com origem um controlador e destino outro controlador, nao vai ter contrato para dar suporte ou comportamento especificado e vai ser definido como best-effort
- [feito] modificar o comportamento para identificar quando eh um controlador, pois eh possivel saber que eh um controlador porcausa que esse ip ja gerou um icmp 16 recebido.
- assim, se for um ip de controlador, na origem ou destino, definir que deve ser enviado pela fila de controle
- [feito] o mesmo ocorre quando os pacotes do contrato passam entre dominios que ficam no caminho entre controladores, vai ter de ocorrer a comunicacao tcp (ida e volta) arrumar isso para quando receber o icmp 15 criar a volta tbm


************** [FEITO] - otimizar trocas de contratos  :
- icmp 15 tem que ser capaz de informar os elementos identificadores do contrato (depende da versao do contrato implementada: ip_src,dst(que esta no destino do pacote, nao precisa ser nos dados),porta e tos)
- icmp 16-reply informa o tos que o controlador possui, se nao tive tos (nao tem o contrato), responde com o campo vazio ou -1
- quando o controlador recebe o icmp 16-reply, verifica se o tos eh o mesmo que ele possui, se for, nao envia, se nao for, entao envia


************** [ARRUMADO] - controladores se comunicam pela interface lo entre si:
- comunicacao controladores-host acontece pela interface correta e dentro do ambiente mininet
- comunicacao controlador-controlador acontecendo pelo loopback? Na vida real os controladores estariam em ambientes/computadores diferentes, e isso nao ocorreria, nao seria necessario tomar a acao abaixo...
(a troca de icmps ocorria dentro do ambiente mininet pq sao pacotes INJETADOS (criados com o openflow) - nao sao pacotes com origem no ROOT/CONTROLADOR, mas os contratos tem origem no controlador e nesse caso ocorre um problema, pq vao por fora do mininet)
(no caso seria necessario essa traducao apenas no caso onde os pacotes tem origem no controlador -> envio de contratos)

- [Verificar] tabelas route + arp (parece td certo e ainda nao encaminha corretamente (c1 ping 10.123.123.2 vai pelo lo))
- [Verificar] ip tables e firewall (firewall nao se, mas ip tables esta limpo)
- [outra ideia] verificar a possibilidade de criar hosts remotos, assim, os hosts root1 e root2 poderiam ser criados remotos como container, assim, cada um teria sua tabela de route
- [IDEIA ESCOLHIDA] criar uma logica de remarcacao, com um ip que obriga a enviar pelo ambiente mininet: rotas para um ip inventado, com MAC do controlador destino, entao no switch remarca esse ip inventado pelo do controlador destino (meio que gambiarra):
[(essa parece a mais facil e rapida de implementar)]
	|->> como todos os controladores estao fora do ambiente mininet, eles usam as mesmas tabelas de arp e route, assim definir uma interface destino para cada endereco nao vai ser possivel.
	|->> criar um endereco ficticio para cada controlador e em cada codigo fazer com que quando um controlador tentar mandar um pacote para um controlador, usar esse endereco ficticio e criar uma regra de fluxo para alterar esse endereco no endereco correto.
	|->> na topologia, criar uma entrada na tabela route e na tabela arp com os enderecos ficticios + mac real
	|->> no momento que for necessario enviar um pacote para um controlador de ip X, sera traduzido esse ip para um ficticio Y e colocado no destino do pacote e aliado a isso, no switch vai ter uma regra para retornara esse ip Y para X, assim, o mac continua o correto e sera entregue normalmente
	* [aqui nao eh necessario pois o pacote eh criado e injetado com o openflow] aplicar a traducao de ip + regra de remacarcar campo de ip em send_icmp + acao de mudar o ip
	* em addRegra mas se o controaldor nao for o destino = nao precisa
	* [aqui precisa com certeza == unico lugar onde o controlador/root precisa enviar pacotes para outro controlador a partir de sua interface] enviar contrato - mudar o ip destino na hora de enviar o contrato
	* caso a remarcacao na origem ainda resulte em problemas, trafegar em todo o percurso com ip ficticio e apenas no destino-ultimo ip antes de chegar no controlador, fazer a traducao/remarcacao

[feito] Ao inves de toda aquelas modificacoes - apenas criar uma tabela de pre-marcacao, onde tudo que tem destino/origem o controlador, remarca para o ip ficticio.
[agora funcionando c1_v2]: os contratos sao enviados pela rede mininet e nao por "fora" como no c1_v1 

# para remarcar actions = [parser.OFPActionSetField(ip_dscp=ip_dscp)]

*** trafego bate na interface mas o root nao responde :::::: ver o que esta ocorrendo + pensar em outras solucoes
(caso isso nao se resolva o tempo de trafego dos contratos nao sera corretamente calculado)
- provavelmente pq o socket tcp pega o endereco ip da origem para realizar o handshake, e no caso o endereco origem eh o endereco do controlador - e ai tem todo aquele problema - tentar mudar o endereco origem
- mudar o endereco origem na hora de enviar os contratos...
** solucao implementada (descrita lá embaixo): foi definido um ip ficticio para cada controlador- cada controlador possui um ip ficticio para outro controlador destino - pois todos os controladores utilizam a mesma tabela route e o ip definido na topologia eh levado como localhost
|-> foi criada uma tabela de pre-marcacao nos switches, que altera o ip origem para o ficticio quando se envia, e altera o ip destino ficticio para o original no recebimento - para que possa responder corretamente - assim, foi so adicionado uma tabela antes das que ja existiam marcacao/encaminhamento - o comportamento padrao eh enviar para a tabela de marcacao



************** [FEITO] - no packet_in :: reinjetar o pacote fora do alocarGBAM

************** [FEITO - nao testado completamente] além dos codigos dscp, verificar se as regras sao removidas corretamente
-obs: fluxos que estao emprestando, sao colocados no vetor de mesma prioridade so que na outra classe, no entanto, mantem os dados de classe, 
prioridade, banda e tos iguais ao original, a ideia eh que ele seja colocado na fila original, mas seja descontado da largura de banda total,
 na fila emprestada - isso na verdade tem um problema, pq o htb vai entender que a fila que emprestou nao esta usando aquela parte da banda e
  vai distribuir para todas as outras filas, inclusive a de best effort - o melhor seria ter um tos equivalente e colocar na outra
  classe - por agr fica assim msm.
  -- solucao nao implementada: so emprestar largura de banda entre classe 1 e classe 2, nao permitir que a fila de best-effor emprestar banda, nem a de controle
  -- o melhor seria, colocar o fluxo que esta emprestando, na fila da classe a qual se empresta.
  - [solucao] - ter tos equivalentes nas duas classes e quando for emprestar, mantem os dados, mas muda o tos - assim, o fluxo vai para a fila correta, na qual se empresta
  Entao, para remover, remove pelos campos - ip, porta
  

************** [FEITO opcao 2 - nao testado completamente] ou pensar sobre - so criar as regras se todos os switches da rota aceitarem os requisitos do contrato/fluxo?:
- no momento, para cada switch eu aloco espaco (salvo no vetor da classe no controlador) e crio as 
regras, caso algum deles nao aceite, os outros switches vao ter de esperar a regra criada expirar para entao liberar 
espaco. - por agora fica assim mesmo, ou entao salvo a saida de cada alocarGBAM e entao se nenhum recursar, ai sim criar as regras

[desenvolvimento]
 ---> duas opcoes:
(1 - primeira) fazer a verificacao se existe espaco para alocar o fluxo em cada switch e caso um nao aceite, rejeitar - passando todos os processos de:
		1-tem espaco suficiente na classe?
		2-tem fluxos suficientes emprestando, para remover ?
		3-tem espaco na outra classe?
		4-tem fluxos de menor prioridade na classe original?
	E entao se todos os switches retornarem positivo para essas perguntas, repetir os processos para entao alocar - no caso, eh preciso repetir para saber quais regras de fluxos sao necessarias remocao
	|->Um alocarGBAM que nao cria regras, so para ver se tem espaco + um alocarGBAM para alocar

(2- segunda) durante a verificacao, salvar a acao que deve ser tomada para cada switch - por exemplo - s1, deletar [regra1,regra2,regra3], s1,alocar [regra1] classe 1,p1,emprestando=0
E entao, se todos os switches retornarem positivo para a verificacao, comecar a aplicar as acoes.
 Teria que ser tipo uma classe, com o nome do switch, int codigo, vetor de regras - algo assim
	- se a verificacao for positiva (todos aceitam o fluxo) - chamar a funcao porta.delRegra(origem, destino, tos) em cada switch - para nao aceitar regras
	repetidas - remover antes eh util se a regra que estou tentando alocar ja existe, entao eh melhor remover antes que tenho ctz que vou conseguir colocar a nova.
	|-> so um alocarGBAM que retorna as regras para remover e criar de cada switch, que sao armazenas em formas de acoes (uma classe) e:
		- se todos os switches retornarem acoes: executar todas as acoes (criar e remover as regras corretamente)
		- se algum switch retornar um vetor de acoes vazio, quer dizer que nao eh possivel alocar o fluxo, entao, nenhuma acao eh tomada (nenhuma regra criada), e o fluxo vai ser descartado.

	- acoes do alocarGBAM:
		- se tiver espaco suficiente na classe original - alocar o fluxo e criar as regras

		- obter os fluxos que estao emprestando largura de banda na classe original, verificar se eles fornecem banda suficiente - remover os fluxos, alocar o novo e criar a nova regra

		- se tiver espaco suficiente na outra classe - alocar o fluxo e criar as regras

		- verificar na classe original se existem fluxos com menor prioridade o suficiente - remover essas regras
		}}

************** [FEITO] criar novos codigos dscp:
- no momento, quando se quer emprestar largura de banda da outra classe (ex classe2), a regra é criada para a fila da classe
original, mas é salva no vetor da fila que emprestou, na classe do switch no controlador.
No entanto, na pratica, esse fluxo estará na fila original, que já está sem banda disponível, assim utilizando mais largura
de banda do que é garantido pela fila orinal dele, utilizando a largura de banda extra de outras filas.
Mesmo o controlador garantindo que a banda foi emprestada e a fila que emprestou não utiliza essa partição, na prática, o htb
distribui essa banda entre as outras filas que solicitam, de forma que a fila de best-effort e a fila da classe que emprestou 
estarão competindo por essa banda e não transferindo para a fila que solicitou o emprestimo.
- Para resolver, é proposto estender os códigos dscp para que cubram as duas classes e que os fluxos tenham códigos equivalentes 
para seus requisitos entre as duas classes. Assim, não é necessário colocar na classe do switch que emprestou no controlador e no 
ovs colocar na fila original, pois eh so trocar o dscp pelo equivalente e colocar na fila em que emprestou.
--- o explicacao confusa ... melhorar
-[solucao] duplicar os códigos dscp e criar as regras para a fila que emprestou, com a meter correta equivalente - classe e prioridade ficam iguais o original, mas o tos fica o equivalente


************** [FEITO] Novo delRegras:
- como agr um fluxo pode estar emprestando e armazenado no vetor da outra classe, entao um fluxo de prioridade 1, classe 1 originalmente, pode estar armazenado com prioridade 1, classe 2 emprestando
- entao, para remover um fluxo eh preciso testar nas duas filas, p1c1 e p1c2

************** [FEITO] Quando receber um contraot, poderia so enviar a mensagem de deletar regras nos switches caso essa regra esteja ativa (exista nos vetores da classe switch):
- verificar o retorno do delRegra - que se encontrar a regra nos vetores, retorna positivo - assim, caso o retorno for positivo - remover no switch.

************* [FEITO] CRIAR um mecanismo para modificar configurações de contrato:
[implementado no momento]
- cada host determina pelo contrato os requisitos de seus fluxos para que a emissão seja com QoS
- no entanto,o host que recebe os dados nao define os requisitos para receber.
- neste caso, se o host precisa dos dados com maior urgencia é preciso um mecanismo para que ele possa editar o contrato de
emissão que configura o fluxo que recebe.
- pode ser feito modificando o campo de dados do pacote icmp - informando que quer modificar o campo de prioridade do
contrato e so ocorre se o end. ip for igual ao end. destino do contrato e tals.
- [solucao] foi implementado um mecanismo que verifica se ja existe um contrato com os mesmos campos de ips e 
porta (no momento porta nao foi implementado), se existe, remove e adiciona o novo - que tbm se configura como
um mecanismo de modificar contratos.

************ [Arrumado] VERIFICAR se o remover regra do switch esta funcionando !!!
- agora estah

************* [ARRUMADO] Deletar regras na tabela de classificacao/marcacao:
- quando se define um novo contrato, alem de deletar as regras dos switches referentes a encaminhamento, no primeiro switch da rota tbm eh preciso deletar a regra de 
marcacao, pois uma nova sera criada
- implementar para a funcao que escuta os hosts e para a que escuta os controladores


************* [ARRUMAdo] alocaGBAM criando regras repetidas ?:
- verificar pq nao esta bloqueando ou removendo regras antigas, antes de criar uma nova - tinha sido implementado
- [testar isso] foi arrumado: antes quando chegava um novo contrato, se verificava se existiam regras com os mesmos ips e prioridade nas duas
classes, pq pode estar emprestando - mas, caso chegue um contrato que tenha os mesmos ips mas com prioridade diferente e classe
é necessario que remova uma regra igual mas que esta em outro vetor, por assim dizer.
- para resolver - agora eh verificado em cada vetor, onde achar a regra, remove, independente da classe e prioridade
- assim, pode armazenar a nova regra onde precisar.

- na verdade, precisa checar antes de aceitar o contrato - se nao tiver contratos repetidos, nao tenho regras repetidas.
- alem disso, remover o contrato anterior, a regra na classe switch e no switch ovs.

-- o tos nao vai dar match pcausa daquele tratamento que o ovs faz - converte o tos 5 pra 21 por exemplo - tem que adaptar
para a regra delRegraF dar o match corretamente  - testar os prints - problema era na definicao do tipo de pacote foi pego
a constante correta agr eth_type=ether_types.ETH_TYPE_IP

- [solucao] quando chega um contrato - eh verificado se existe um outro ja salvo com os mesmos campos, no momento ip_src e ip_dst, e remover 
o contrato e as regras associadas - na classe switch e na tabela do ovs (de marcacao e encaminhamento).
- isso tambem ja serve para o processo de atualizar contrato - so teria que ter um mecanismo de seguranca para permitir que apenas os autorizados modificassem um contrato.

--- esta funcionando mas precisa adaptar para quando utilizarmos portas nos contratos...(remove todas as regras -em todas as tabelas- referentes ao ip_src e ip_dst informado)


************* [Feito - talvez precise dar mais uma olhada] Conexoes ficando abertas - O processo de envio e recebimento de contratos para fechar a conexao apos receber:
- enviar tbm a quantidade de contratos
- assim, apos receber a quantidade definida, encerrar a conexão
- so precisa fazer no envio de contratos entre controladores, pq os hosts sao limitados a enviar um por vez, no momento
 
************* [ARRUMADO] O send contratos está concatenando vários contratos em um pacote e enviando:
- ou dividir os contratos em um por pacote, ou dar um jeito de separar esses contratos do outro lado


************* [ARRUMADO] enviar contratos do controlador nao envia multiplos contratos, ou nao recebe multiplos contratos:
- quando envia, diz que esta enviando varios contratos, mas quando chega, chega so um...

------>>>  [resolvido] icmp dando erro ?? - "struct.error: required argument is not an integer"
- não estava dando erro antes.... resolver --- aparentemente a porta de saida deveria ser int e estava chegando str
[arrumado] >> foi alterado a forma de salvar as rotas, agr a porta é um inteiro


------>>> [resolvido] addRegraC não funcionando ?? TypeError: unsuported operand types.... >>> provalvemente é problema com [resolvido]
o tipo de dados do tos. Na definição diz um inteiro de 8bits e estou usando como inteiro.
- na verdade acusa erro no match?
[corrigido - foi preciso definir que o tipo de pacote era tcp]

------>>> [resolvido] addRegraC não está dando erro, mas não cria a regra de fluxo ?? erro ou no actions (deve ser nw_dscp algo assim na remarcação, ao inves de ip_dscp) ou no instructionsactions
-substituindo para nw_tos a regra é criada, mas não foi testado. Deve estar funcionando

------->>>> [resolvido] addRegraF não está dando erro, mas não cria a regra de fluxo ?? pode ser que o ip_dscp tenha que alterar para nw_tos
-- aparentemente o problema está na parte de incluir o meter_id

------>>>> talvez seja necessário armazenar os contratos que estão ativos:
-- regras de marcação ativas são baseadas nos contratos ativos. No entanto, quando um novo contrato deve 
reescrever essas regras é preciso que as regras de marcação sejam substituidas - ou seja, um contrato deve deixar
de estar ativo para que outro o substitua - e o controle teria de saber qual contrato está ativo e quais regras de
marcação estão ativas ---- pensar mais um pouco sobre


 *************** [feito/nao testado] O alocarGBAM - onde colocar as regras que emprestam e seu tos ---- regras que precisam emprestar, nao devem alterar seu tos. As regras emprestam largura de banda da classe e é salva na fila dessa classe, mas a regra 
de criação no switch ovs deve ser para a classe original. Isso faz com que o emprestimo seja garantido e que os requisitos do fluxo sejam garantidos. Pois, classes diferentes possuem
tos diferentes que podem ser incompativeis. Ex: existe um tos para classe 1 com 1000kb de banda, prioridade 1, mas não existe na classe 2. Assim se emprestar, não tem um tos na classe 2
equivalente. A solucão foi manter o tos, mas salvar na fila da classe da qual se empresta com uma tag emprestando, criando a regra como se fosse na classe original. MAS NAO FOI ARRUMADO NA IMPLEMENTACAO AINDA.

- além disso, é preciso criar as funcoes de remover regras nos switches, quando for necessário substituir fluxos.

*************** [feito/nao testado] alocarGBAM - não criar regras repetidas ---- Quando um packet_in ocorre e uma regra de fluxo é criada, é adicionada a cópia na classe do switch no controlador. Quando as regras nos switches expiram, as regras são removidas 
nos switches e avisadas ao controlador para remover da classe switch. No entanto, pode ocorrer de alguns switches removerem antes de outros e se ocorrer outro packet in com criação de regras nesse meio tempo
pode ser que duas regras iguais sejam criadas na classe do switch do controlador, fazendo com que consuma duas vezes a largura de banda.
-- Solução, antes de adicionar uma regra nova em cada switch ovs da rota, verificar se ela ainda não existe, caso exista, apenas criar a regra no switch ovs. -- Obs: talvez nem fosse necessario criar a regra nesses switches,
pois é como se ela ainda existisse.;; optando por não criar a regra nestes casos !!!!
[resolvido, antes de alocar um fluxo ele é testado no delRegra da porta, assim se já existir uma regra de fluxo, ela é removida e realocada -- PODE NAO SER A MELHOR SOLUCAO]


************** [feito/não testado] ICMP/contratos - encaminhamento de ICMP 15 e 16 com regras (criar regras):
--->>>quando um ICMP inf. request chega no domínio, o primeiro switch analisa o pacote e encaminha para o controlador.
- o controlador analisa quem enviou e responde com um ICMP inf. reply. 
[precisa criar as regras para receber os contratos vindos da origem pelo caminho de switches até o switch que 
possui conexão com o host do controlador - com um idle timeout de 10s - algo assim]

- o controlador dá sequencia no ICMP inf. request enviando pelo último switch do caminho.

--->> quando um ICMP inf. reply chega no domínio, o primeiro switch analisa esse pacote e pela origem ser de um 
controlador desconhecido, vai enviar para o controlador do domínio decidir o que fazer.
- caso o destino fosse o controlador que está analisando o pacote, são enviados os contratos para o destino 

[SOLUCAO: o controlador que encaminha um icmp 15 (inf.req) que não tem origem nele precisa criar regras para encaminhar
respostas icmp 16 em direção ao controlador que originou o icmp, ou seja, em todos os switches da rota e pela fila de controle
 - sim é preciso, pelo menos com um tempo idle suficiente - pois logo não se utiliza mais
 ]
 
[pt2 SOLUCAO: tem que criar a regra para enviar os contratos tbm - mas sem um pacote icmp 16, não tem como saber a origem, assim
é preciso que o icmp 16 gere um packet_in. Então as regras de encaminhamento para as respostas icmp 16 e envio dos contratos
devem ser criadas após o controlador receber o icmp 16. Neste caso, não é necessário criar regras para respostas icmp 16,
pois no primeiro switch o controlador identifica o pacote e injeta no switch da borda mais próxima do destino e aproveita
para criar as regras de encaminhamento dos contratos vindos do ip_controlador original (destino do icmp 16) para o
ip_controlador gerador do icmp 16 (origem do icmp 16) - com um idle timeout suficiente para enviar os contratos
]

### obs isso deve ser testado após funcionar para um domínio (alocar e estabelecimento de contratos).
[OK - A PARTE DE RECEBER E TRATAR UM ICMP 15]
[A PARTE DE RECEBER E TRATAR UM ICMP 16, quando:
 - não é o controlador destino;
 OK - é o controlador destino;
]


************* [ARRUMADO] ICMP/contratos = verificar se é possível acesar os dados do icmp (inf. reply 16) respondido em um controlador. 
- tem um monte de lixo junto no campo de dados do pacote icmp
- achar um jeito de enviar sem lixo/filtrar o lixo


************* [feito/nao testado] alocarGBAM [criação de regras e alocação de banda] -- estou alocando duas vezes largura de banda, uma ida e uma volta - e duas regras para cada fluxo
- é desejado que a ida e a volta utilizem a mesma largura de banda ? ou que cada um determina quanto vai enviar ?
- pensando assim, faz sentido cada um determinar quanto vai enviar
- neste caso, so se cria a marcacao na ida sempre.
- esse problema so esta associado com fluxos de classe 1 e 2 - fluxos de classes 3 e 4 precisa sempre criar regras de ida e volta.
[solucao - so cria as regras de ida sempre
- um contrato so estabelece os requisitos de QoS para envio de dados]

 
 
************* [ARRUMADO] o controlador está se enviando pacotes icmp inf. req. e respondendo inf. reply para si mesmo:
- entender pq isso esta ocorrendo
- estava errado o ip_dst quando chamava o send_contratos - estava com o ip do controlador que recebia o icmp 16, e devia ser o ip_src.
- assim, o controlador se enviava os contratos e gerava novos icmp 15 até quebrar devido ao problema de estar sendo concatenado varios contratos na mesma msg algo assim.
- Tbm, criei outra funcao para receber contratos, especifica para comunicacao entre controladores. Antes, a funcao tinha sido pensada para hosts,
logo, um contrato era recebido, as regras de marcacao e encaminhamento eram criadas nos switches da rota e um icmp inf. req. 15 era gerado
para descobrir controladores na rota e disseminar o contrato.
- no entanto, quando a comunicacao eh entre controladores, o protocolo atual implementado diz que apenas o primeiro controlador que admitiu o contrato gera um icmp e todos
os outros controladores respondem para ele, que assim, envia os contratos. Entao, na funcao de admitir contratos entre controladores, nao deve ser gerado um icmp inf. req. apenas
criado as regras. :) (controladores se comunicam pela porta 8888 e com hosts pela porta 4444)


************ [FEITO - mas de um jeito meio errado] MODIFICAR - ICMP/contratos: no momento que o contrato é definido agora já é possível obter os switches da
rota e assim fazer os processos alí mesmo, sem depender de packet in:
- O controlador que recebe o contrato pode criar as regras de encaminhamento e marcacao nos switches da rota
- no entanto, com o contrato atual, nao se pode enviar o icmp, pois o controlador nao conhece o endereco MAC do destino, que seria o host final.
- o que se pode fazer eh inventar um endereco mac, pois a ideia eh que o pacote seja aproveitado pelos controladores da rota, mas seja descartado pelo host final.

************** [feito] ip_dscp na regra de encaminhamento fica 28, mas na de marcação fica 112 ?
[corrigido - ip_dscp adiciona os bits nos primeiros, [000000]00, fazendo com que seja interpretado errado
- usando nw_tos os bits são adicionados nos últimos 00[000000]]
- a funcao de modificacao de set_field trata ip_dscp de uma forma diferente da funçao match. No entanto, tratam
de forma igual o nw_tos, assim esse é usado.

************** [feito] revisar a criacão de regras, pois não está ocorrendo match na regra de encaminhamento !!!
-- eh pq eu estava colocando match apenas com pacotes tcp, e estava testando com pacotes ICMP.
-- com tcp é importante para testar portas, que é o foco do contrato (ip_src, ip_dst e porta).
- foi alterado para não limitar ao tipo tcp no match

************** [ARRUMADO] regras de encaminhamento (tabela 2) com meter_id, não estão sendo criadas !!
- rever a criacao das meter_bands
- [solucao] Foi utilizada a maquina virtual do mininet tutorial com ovs 2.13.1 - aparentemente a versão ovs que eu compilei
na vm ubuntu server estava incorreta mas o ovs da vm do mininet foi compilado corretamente.
- a partir da versão ovs 2.10 as meter tables já são suportadas.



************** [RESOLVIDO - ver PROBLEMA host fora do namespace mininet não responde pacotes]
		{
		****** ARRUMAR -- codigo python para configurar/enviar um contrato entre host e controlador funciona, mas:
			- tem que ver as rotas nos roots
			- rotas e arp devem estar configurados corretamente: enderecos IP e MAC e interface destino deve ser a interface de saida do controlador ex root1-eth0
			- deste modo, os hosts conseguem enviar os contratos (estabelecer conexao com o socket)
		****** [ARRUMADO] ARRUMAR Criar as regras de encaminhamento de contratos para o root correspondente:
			-- criar em todos os switches, rotas para o root (controlador) do dominio
			- Regras de encaminhamento pela classe de controle - sem marcacao pq se o destino eh o controlador, entao a classe eh de controle
			------ As regras estao criadas e enviam os pacotes para o host, mas o host está ignorando os pacotes
			************** [ARRUMADO][ARRUMAR Código de adicionar/tratar contratos pelos hosts morreu, só funciona fora do ambiente mininet:
- estava funcionando na antiga VM, mas na mininetVM bugou.
		}




************** [FEITO] Atualmente pacotes que são enviados via packet in para o controlador não são renjetados no switch (são perdidos):
	- após criar as regras reinjetar os pacotes no switch.
	- os icmps inf. req. e inf. reply já estão sendo reinjetados.
	- foi criada uma funcao que eh chamada no AlocarGBAM -
#funcao injetar pacote - o pacote que gera o packet_in as vezes, em determinados switches, precisam ser reinjetados
#principalmente no switch que gerou o packet in ou no ultimo switch da rota
#Mas ha casos em que as regras precisam ser criadas nos switches da rota e ser injetado apenas no ultimo, assim, precisa fazer o tratamento


************* OBSS: É DESEJÁVEL QUE O CONTROLADOR SEJA VISTO COMO SE ESTIVESSE CONECTADO DIRETAMENTE A APENAS UM 
SWITCH DO DOMÍNIO - EVITAR COMANDOS "MÁGICOS" [impossível no estado atual do openflow - as regras são configuradas
como se existisse um link entre controlador e cada switch.
- no entanto a comunicação com hosts é feita somente pelo switch que está conectado a ele.


************* OBSS: Separar os diagramas do controlador, por exemplo em:
- diagrama de troca de contratos (toda a parte de icmp e envio de contrato e criaçao de regras), diagrama de
tratamento de pacotes em geral (toda a parte de verificar contrato, alocar banda e criar regras) 


************* OBS: Poderia criar uma GUI para cada controlador :
-  o controlador teria um icone para cada switch do seu dominio:
-- quando o switch fosse acessado, seria mostrado as regras criadas de cada fila e a banda total utilizada (no momento as regras para as filas de controle e best-effort nao sao armazenadas, mas poderia mudar)
-- pensar sobre - deixar mais para o final caso seja interessante.

######################################################################################################
############################################## TESTES ################################################

- [ok] testar se as regras são salvas na classe switch do controlador
- [ok] testar se as regras adicionadas diminuem a quantidade de largura de banda disponível corretamente
- [ok] testar se as regras são atualizadas/removidas corretamente conforme a label
- [ok] testar se eh possivel colocar o endereco ip_dst do host no icmp inf. reply.
- [ok] testar se eh possivel recuperar o endereco ip_dst do host no icmp inf. reply no controlador destino do reply
- [ok-vm mininet] se em outra vm existente, o código das meter table não estava funcionando - observar a versão do ovs
- [ok] armazenar regras corretamente
- [ok] atualizar o controlador com as regras removidas nos switches
- [ok] se o controlador consegue remover as regras nos switches (alocarGBAM: caso de remover regras q estao emprestando ou possuem menor prioridade )
- [ok] regras de marcação corretas
- [ok] regras de encaminhamento corretas (nao precisa ter testado se a meter esta funcionando)
- [ok] regras de encaminhamento de pacotes icmp/contratos pela fila de controle
- [ok] troca de contratos entre controladores estar funcionando corretamente
- [ok-nao precisou na vm-mininet] arrumar as regras meter (adaptar para tc-flow/tc-flower ?)
- [ok] testar se eh possivel enviar pacotes utilizando datapaths salvos dos switches


- [ok] testar se as regras de emprestimo são criadas corretamente
- [verificar] testar se eh possivel gerar tráfego com wireshark/tshark conforme as bases de dados


--- usar geradores de tráfego para utilizar bases de dados IoT e injetar na rede:
[base de dados: - https://www.stratosphereips.org/datasets-iot23#:~:text=IoT%2D23%20is%20a%20new,ranging%20from%202018%20to%202019.
]

[links: - (da pra usar o tshark para injetar pcap) https://tshark.dev/generation/program_gen/
		- (um exemplo gerando) https://forum.mikrotik.com/viewtopic.php?t=168534
		- (lista de geradores) https://www.dnsstuff.com/network-traffic-generator-software
		]


################################################################################################################
#########################################         EXPLICACOES			########################################	
*** explicação do pq re-injetar o pacote icmp 15 no último switch do caminho:
- um switch mais na borda dispara um packet in e envia o pacote para o controlador
- quando um controlador aceita um fluxo (atual) ou estabelece um contrato (em dev.) é gerado um icmp 15 (inf. req.)
para descobrir os controladores ao longo do caminho.
- se esse icmp 15 fosse injetado no switch mais da borda próxima do host que enviou o pacote do fluxo a ser aceito,
precisaria que fosse criado regras para encaminhar o icmp em cada switch da rota, para enviar UM único pacote icmp,
que poderia não ser sincronizado o suficiente e gerar novos packet_in para o próprio icmp 15.
- Assim, injetando o pacote no switch mais da borda próxima do destino, não é necessário criar regras ao longo do 
caminho para tratar esse único pacote.

- o pacote icmp 16 (inf. reply.) tbm não precisa de regras:
 - quando um icmp 16 chega no primeiro switch do domínio, ele é analisado. Caso seja para destino o controlador
 desse domínio, os contratos são enviados com direção a origem do pacote.
 Caso não seja, injetar no switch mais próximo do destino, e criar as regras nos switches do caminho para que
 quando o controlador destino enviar os contratos, esses passarem pela rota no domínio.
 
 - Isso não é possível de fazer no packet in do icmp 15, pois não se sabe quem é o controlador destino para
 onde se enviam os contratos. Mas se aproveitando do icmp 16, a origem é o controlador que requisita os contratos
 e o destino é o controlador que gerou o icmp 15 e possui os contratos.
 
- Re-injetar os pacotes icmp é necessário pois um packet_in subtrai o pacote (agr não me lembro com certeza disso, mas é quase 100%)
- Re-injetar no último switch de um caminho evita criar regras para trafegar apenas um pacote e arriscar de gerar mais packet_ins.


################################################################################################################# 
########################################		PROBLEMAS		#################################################

*********** [ARRUMAR] Absolutamente do NADA - nao consigo mais iniciar nenhum controlador dentro de um root (host fora do ambiente mininet); fora disso, consigo
- cara, nao mexi em nada acho, so estava arrumando o x11forwarding antes - lembro de no maximo ter modificado chmod 800 xauthority ; algo assim
- esta dando erro de sintaxe de alguma coisa do python2.7/tinyrpc
- foi instalada a versao python3 do ryu $ sudo apt-get install python3-ryu (nao funcionou: mesmo erro)
- foi reinstalado o tinyrpc:: $ sudo unistall tinyrpc
- $sudo pip install tinyrpc==0.8

*********** [resolvido] PROBLEMA COM X11 FORWARDING no mininet:
  - se isso acontecer dnv (do nada essa parada volta sei la) usar a solucao de adicionar o display remoto com autoridade root:
  - https://stackoverflow.com/questions/67319171/x11-connection-rejected-because-of-wrong-authentication-in-mininet

*********** [resolvido] PROBLEMA host fora do namespace mininet não responde pacotes direcionados para ele; ou; nao alcançavel; ou ; da ping mas nao responde:
*********** [resolvido] PROBLEMA host fora do namespace usando interface errada para se comunicar:
 ************** [resolvido] Código de adicionar/tratar contratos pelos hosts morreu, só funciona fora do ambiente mininet:
	- os dois problemas acima possuem a mesma solucao: revisar as tabelas de route e arp
	- primeiro problema: nao responde o pacote, mas ele chega na interface - end. MAC errado - arrumar a tabela arp no emissor
	- primeiro problema: nao alcancavel - revisar as regras de encaminhamento e as tabelas arp/route
	- segundo problema: os hosts fora do espaco mininet utilizam todos da mesma tabela, assim, a primeira entrada que tiver sera usada - ou deixar apenas um match para cada entrada ou ficar excluindo e adicionando quando for usar...



*********** [resolvido] COMPATIBILIDADE Meter_table:
*https://docs.openvswitch.org/en/stable/ref/ovs-actions.7/?highlight=meter#the-meter-action-and-instruction
	- Open vSwitch 2.0 introduced OpenFlow protocol support for meters, but it did not include a datapath implementation.
	Open vSwitch 2.7 added meter support to the userspace datapath. Open vSwitch 2.10 added meter support to the kernel datapath.
	Open vSwitch 2.12 added support for meter as an action in OpenFlow 1.5.
	
*https://docs.openvswitch.org/en/stable/howto/tc-offload/?highlight=meter
	- em uma versão do ovs (talvez tenha que atualizar a minha para 3.0), foi adaptado para suportar meter table com linux tc
	- tem o tutorial

* da pra criar regras "meter" com tc:
Bases:::
-- listar regras ingress: tc -s -d filter show dev s1-eth1 ingress
-- listar tc filter show dev eth0 ingress
	**https://man7.org/linux/man-pages/man8/tc-flower.8.html
	**(TOP)http://www.openvswitch.org/support/ovscon2017/horman.pdf
	**https://man7.org/linux/man-pages/man8/tc.8.html
	**(TOP)https://man7.org/linux/man-pages/man8/tc-police.8.html
 - vai dar trabalho
 - observando no espaco de usuario com tcpdump, os pacotes possuem os mesmos ips - eu tinha dito que era tudo por loopback e coisa e tal, n sei agr o pq pensava assim (deve ser loopback, mas os ips mantem sla)-
 - posso criar filtros na origem, que simulam o limite/meter - explorar melhor o tc-flower e o tc-flow ver como usar os dois
 - criar os filtros para limitar conforme o tos
 - como usar tc-flower e habilitar o tc para remover pacotes da interface - http://www.openvswitch.org/support/ovscon2017/horman.pdf 
 - aqui tem um exemplo usando tc-police para tráfico ingresso - que é a abordagem a ser seguida agr - https://man7.org/linux/man-pages/man8/tc-police.8.html
 - a ideia é que os pacotes que chegam por uma porta (ingresso) devem ser limitados pela banda conforme o tos definir.
 ---- a regra tem que ser nesse estilo:
 tc filter add dev eth0 protocol ip parent ffff: \
 flower ip_proto tcp dst_port 80 \
 action drop
 ++ juntando com um action:
 tc qdisc add dev eth0 handle ffff: ingress
 tc filter add dev eth0 parent ffff: u32 \
                   match u32 0 0 \
                   police rate 1mbit burst 100k

:::: (nao aparenta estar limitando) sudo tc filter add dev s1-eth2 protocol ip parent ffff: flower dst_ip 172.16.10.1 action police rate 1mbit burst 100k
:::: (nao aparenta estar limitando) sudo tc filter add dev s1-eth1 protocol ip parent ffff: flower dst_ip 172.16.10.2 action police rate 1mbit burst 100k drop


-- essa regra funciona (drop tráfego ingresso na porta s1-eth2 - nao pega nem no tcpdump):
 --- sudo tc qdisc del dev s1-eth2 ingress
 --- sudo tc filter add dev s1-eth2 protocol ip parent ffff: flower dst_ip 172.16.10.2 action drop

--- adaptando para medir o rate :::
nao funcionou ainda  -- apenas o drop esta funcionando
: sudo tc qdisc add dev s1-eth1 handle ffff: ingress
: sudo tc filter add dev s1-eth1 parent ffff: protocol ip u32 match u32 0 0 action police rate 256kbit burst 100k drop

--- quero usar flower (ainda nao funcionou com flower)
: sudo tc filter add dev s1-eth1 protocol ip parent ffff: flower dst_ip 172.16.10.2 action police rate 256kbit burst 100k drop

-- ovs kernel switch os pacotes são adicionados em hardware e precisa do offload integration, mas com outro tipo de switch (default ou ovs) talvez os pacotes sejam integrados em software e seja possível utilizar tc police.

-- Offload Integration in OvS Included in OvS v2.8 ::: talvez precise dessa versão...
 
 * pelos testes do ryu -- funciona algumas regras meter .. ver isso e adaptar
 
* adaptar o codigo para o ovs da cnpq lá.

* outra alternativa é usar tunel, como o prof falou:
 - um tunel interno ao domínio:
 s1 - s2 - s3 - s4, seria um tunel entre os switches da rota 

 - com tunel da para configurar a largura de banda
 
 ********* Boas informações sobre como lidar com interfaces de rede virtuais e tratar qual interface deve responder cada ip:
 - https://unix.stackexchange.com/questions/589048/server-does-not-respond-to-ping-icmp-is-received-and-nothing-happens
 
 *************************** VERSÃO DO OVS DA VM MININET (VM DO TUTORIAL) FUNCIONAM AS METER:
 - VM MININET -> OVS 2.13.1 ; ryu: 4.34
 - na VM que eu compilei e não funcionavam as regras meter -> OVS 2.13.4 ; ryu 4.34
 - AS solucões trazidas em cima são interessantes e também devem resolver o problema, mas por agilidade, será testado
 na VM MININET os códigos desenvolvidos.
 -- [TESTADO - OK - funcionando :)]
 -- VM exportada (24/09)
										
										
										### FERRAMENTA DE TESTE RYU ###
******** FEITO Teste com a ferramenta de teste de switch do ryu, para verificar que meter table não está funcionando no ovs versão: 2.13.4
-[teste] https://osrg.github.io/ryu-book/en/html/switch_test_tool.html


												### OUTROS ###
******* desenvolver metricas *********:
- overhead de tempo do framework
- escalabilidade
- mostrar que funciona
- reforcar diferenciais
- publicar o codigo com link aberto github (portfólio)


******* Sobre a quantidade de regras de fluxo geradas:
- para cada direcao, um fluxo possui uma regra de marcacao e uma regra de encaminhamento (logo sao 2 regras no maximo por switch, 1 no minimo)
		- a regra de marcacao fica somente no switch mais da borda proxima do emissor
		- as regras de encaminhamento ficam em todos os switches da rota, o da borda proxima do emissor inclusive
- logo, levando em consideracao que exista encaminhamento de ida e volta, serao 4 regras por fluxo.
(existem formas de posteriormente agrupar em prefixos de mesmos requisitos com meter groups e group rules)

####### sem uma conexao direta entre switch e controlador:
### auto off band e inband



				#############################################################
	Tabela 	dscp     --- 	dscp são 6 bits do cabeçalho IPv4, logo se pode utilizar 64 códigos	:

| Aplicações               | Tipo de tráfego (classes) | Banda                                                         |
|--------------------------|---------------------------|---------------------------------------------------------------|
| Voip,streaming,mensagem  | Áudio(1)                  | 4,32,64,128,500                                               |
| chamadas,streaming       | Vídeo(1)                  | 1,2,5,10,25                                                   |
| web,jogos,down/upload... | Dados(2)                  | Iguais classe 1 (foram replicados para melhorar o empréstimo) |
| geral                    | Best-effort(3)            | Não limitado                                                  |
| comunicacao com control  | Controle(4)               | Não limitado                                                  |

####################		Outros			############################

| Classe | Banda | Prioridade | DSCP |
|--------|-------|------------|------|
| 3      |       | 1          | 60   |
| 4      |       | 1          | 61   |

####################		Tabela Classe 1			############################
		
| Classe | Banda   | Prioridade | DSCP    |
|--------|---------|------------|---------|
| 1      | 4kbps   | 1/2/3      | 0/10/20 |
| 1      | 32kbps  | 1/2/3      | 1/11/21 |
| 1      | 64kbps  | 1/2/3      | 2/12/22 |
| 1      | 128kbps | 1/2/3      | 3/13/23 |
| 1      | 500kbps | 1/2/3      | 4/14/24 |
| 1      | 1Mbps   | 1/2/3      | 5/15/25 |
| 1      | 2Mbps   | 1/2/3      | 6/16/26 |
| 1      | 5Mbps   | 1/2/3      | 7/17/27 |
| 1      | 10Mbps  | 1/2/3      | 8/18/28 |
| 1      | 25Mbps  | 1/2/3      | 9/19/29 |

####################		Tabela Classe 2			############################

| Classe | Banda   | Prioridade | DSCP    |
|--------|---------|------------|---------|
| 2      | 4kbps   | 1/2/3      | 30/40/50 |
| 2      | 32kbps  | 1/2/3      | 31/41/51 |
| 2      | 64kbps  | 1/2/3      | 32/42/52 |
| 2      | 128kbps | 1/2/3      | 33/43/53 |
| 2      | 500kbps | 1/2/3      | 34/44/54 |
| 2      | 1Mbps   | 1/2/3      | 35/45/55 |
| 2      | 2Mbps   | 1/2/3      | 36/46/56 |
| 2      | 5Mbps   | 1/2/3      | 37/47/57 |
| 2      | 10Mbps  | 1/2/3      | 38/48/58 |
| 2      | 25Mbps  | 1/2/3      | 39/49/59 |

Por que ter duas classes se possuem as mesmas prioridades e bandas disponíveis?
R: Porque com duas classes, sendo uma voltada para aplicacoes que envolvem streaming/video/audio (classe 1) e outra 
voltada para transaçoes de dados no geral, como download de arquivos, troca de mensagens, e-mail entre outros, é possível 
evitar que os fluxos de uma classe dominem toda a largura de banda reservada e ainda se beneficiem do emprestimo da banda
não utilizada. Isso torna os recursos mais flexiveis, mas disponíveis prioritariamente para as classes definidas.



##############################################################################################################
#						LOGICA DE ENDERECOS IP FICTICIOS - 2 controladores:
				###################################################################


	* os enderecos ficticios serao usados dentro do mininet como sendo os enderecos reais
	* no switch mais proximo do controlador, o endereco ficticio deve ser traduzido pelo real para que a interface correta receba e possa responder

	host: root1-c1 root2-c2

	root1-C1
	TC['10.123.123.1']='10.10.10.1'
	TC['10.123.123.2']='10.10.10.2'
	
	root2-C2
	TC['10.123.123.1']='10.10.10.1'
	TC['10.123.123.2']='10.10.10.2'
	
	route table
		dst			 dev
	10.10.10.1		root2-eth0 (c2->c1)
	10.10.10.2		root1-eth0 (c1->c2)

#unico momento que usa eh para envio de contratos
ip_dst tem que ser trocado e remarcado no primeiro switch, na ida
ip_src tem que ser trocado e remarcado na chegada
#tem que criar as rotas para esse endereco ficticio, como se fosse o ip do controlador mesmo - um ip ficticio eh o ip do controlador dentro do ambiente mininet

	[algoritmo]
-> root1-c1 recebe um icmp 16 -> enviar os contratos
enviar_contratos(src=10.10.10.1, dest=10.10.10.2)

s1 (mais proximo de root1) -> match ip_src=10.10.10.1, ip_dst=10.10.10.2 trocar ip_dst 10.10.10.2 para 10.123.123.2 (para que root2 possa responder)
s1 (mais proximo de root1) -> match ip_src=10.123.123.2, ip_dst=10.10.10.1, trocar ip_dst 10.10.10.1 para 10.123.123.1 (para que root1 possa responder)


**** PARA 3 controladores (nao vai dar tempo de implementar e testar isso, ao menos para o AINA)

host: root1-c1 root2-c2 root3-c3

	root1-C1
	##TC['10.123.123.1']='10.10.10.1' (esse nao precisa pq nao se envia para si mesmo)
	TC['10.123.123.2']='10.10.10.4'
	TC['10.123.123.3']='10.10.10.3'

	root2-C2
	TC['10.123.123.1']='10.10.10.1'
	TC['10.123.123.3']='10.10.10.2'

	root3-C3
	TC['10.123.123.1']='10.10.10.5'
	TC['10.123.123.2']='10.10.10.6'
	
	route table
		dest		dev
	10.10.10.1 		root2-eth0 (c2->c1)
	10.10.10.2 		root2-eth0 (c2->c3)
	10.10.10.3 		root1-eth0 (c1->c3)
	10.10.10.4 		root1-eth0 (c1->c2)
	10.10.10.5 		root3-eth0 (c3->c1)
	10.10.10.6 		root3-eth0 (c3->c2)

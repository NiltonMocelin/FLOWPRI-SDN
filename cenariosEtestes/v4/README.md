- Versão 4 do FLOWPRI-SDN

- Resolvida a questão de teste com multiplos controladores no mesmo ambiente mininet:

-- Antes ( < v3 ): Testando no mininet, os controladores verificavam a mesma tabela de roteamento e assim não sabiam por qual interface encaminhar, pois os controladores deveriam ser capazes de encaminhar pacotes entre si. Como o end IP destino é o mesmo na comunicação C1->C2 e C3->C2, C1 e C3 utilizariam a interface de primeira ocorrencia para enviar pacotes para C2. Solucionamos criando traduções de endereços de modo que cada controlador tenha endereços fictícios para comunicação entre si. Mas essa abordagem é muito custosa para testes personalizados.

-> O linux possui 3 tabelas por padão (local, main e default) e suporta até 255 no total.

-> Resolvemos criando tabelas de roteamento para cada controlador:

* Script adicionado na topologia

- Criar a tabela de roteamento para o controlador C1:

`echo "1 routec1" >> /etc/iproute2/rt_tables`

- Especificar as condições de uso da tabela :

`ip rule add from 10.123.123.1 table routec1`

- Criar uma regra para encaminhar tudo que vem dos controladores para a tabela routecX:

`ip rule add from 10.123.123.1 lookup routec1`

- Nao sei qual a certa se é só table ou precisa ser lookup - com o comando ip rule list parece dar no mesmo.

- Especificar o gatheway da tabela:

`ip route add default via 10.123.123.1 dev root1-eth0 table routec1`


-> Listar as tabelas de roteamento:

`ip route show table all`

`cat /etc/iproute2/rt_tables`

-> Listar as regras de encaminhamento das tabelas de roteamento:

`route -n`

`ip route show table <tabela>`

`ip route list`

`ip rule list`


# Referencias

https://datahacker.blog/industry/technology-menu/networking/iptables/follow-the-ip-rules

http://www.allgoodbits.org/articles/view/24

https://man7.org/linux/man-pages/man8/ip-rule.8.html
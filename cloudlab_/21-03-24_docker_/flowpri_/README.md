# A FAZER 
{
* Configurar a criação das portas e switches no fp_topology_discovery -- configurar o addporta lá
* Descobrir com quem cada porta dos switches se conecta. -- verificar como o topology discovery do ryu faz isso e implementar tbm

* Dar uma olhada no que precisa implementar para o suporte de ipv6
* Implementar uma GUI bonita e com estatísticas

* Testar no cloudlab
* Definir cenários para testes.
* Implementar controladores e comparar QoS
* Escrever Artigo
* Escrever Plano Aula
* Escrever Plano Dissertação
}

* ! foi implementado dhcp == funcionando --> mas precisa mudar para que uma classe rede agrupe os switches participantes + a informacao host(mac+ip) deve ser armazenada com os switches, para saber onde os hosts estao (no caso de cenários sem movimento de hosts)


* poderia propor uma forma de simular filas utilizando meter rules
{
    * poderia controlar divisoes de banda para cada classe utilizando regras meter para emprestar banda entre as classes prioritárias - da forma como ja se faz, praticamente

    * E o best-effort, que seria a problemática neste caso, poderia se criar uma regra meter-group do tamanho da classe, e agrupar os fluxos que utilizariam a mesma meter (pq se duas regras utilizam a mesma meter ==> utilizam a mesma partição-mesmo contador)

    * Em casos onde nao se pode configurar -> poderia se fazer dessa forma

}


* Poderia ter um servidor intermediario para a parte de descoberta de serviços utilizando o esquema de contratos. Apenas para IPv6
* Quando um contrato chega em um domínio, este contrato deve subir ao servidor regional
* quando um pacote chega em um domínio, este deve enviar um icmp inf request para o servidor regional, solicitando um contrato, se existir! (melhor que pedir ao domínio de origem, pois o fluxo pode ser encaminhado por outra rota!!!)


-> interface web ta com problema


-> implementar a parte gui
-> implemetar bgp e a parte de roteamento dinamico

-> criar a versão com trocas de contratos utilizando um servidor terceiro (regional como falei)
-> comparar as versoes em termos de atraso
-> escrever artigo!


## Refatorando 

# Funcionalidades a implementar

 * Burlar NAT: Identificador único para fluxos baseado em conteúdo de pacote -> IPv6 é o jeito mais fácil e rápido!!

 * Substituir esse DSCP por um classificador --- sei la como que vamos fazer isso agora

 * Implementar a descoberta de domínios na rota que utilizam flowpri. (considerando que a rota é estática durante o tráfego do fluxo)

 * Implementar a garantia de QoS -- monitar? ....

 * Implementar o servidor third-party que vai coordenar o QoS as a service. -- todos os controladores da rota precisam informar que fazem da rota e que estao fornecendo qos pra o fluxo devidamente identificado com um identificador unico.  

 * Aplicacao no host informando QoS dos seus fluxos

 * Suporte a redes virtuais --- por último....

## Ordem de desenvolvimento{

* --- Algumas coisas já são existentes só colocar para ficar mais funcional

*  #Resolver a parte de configuracao manual

* #Implementar DHCPv4 (feito) e v6 ()

* #Resolver a parte básica de roteamento.... (descoberta de topologia)

* #Resolver a parte de suporte a IPv6.

* #Resolver a parte de classificacao

* #Resolver a parte de garantia de QoS.

* #Resolver a parte de monitoramento de QoS.

* #Resolver a parte de QoS as a Service.

}
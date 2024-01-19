# Nao testado

## Refatorando 

# Funcionalidades a implementar

 * Burlar NAT: Identificador único para fluxos baseado em conteúdo de pacote

 * Substituir esse DSCP por um classificador --- sei la como que vamos fazer isso agora

 * Implementar a descoberta de domínios na rota que utilizam flowpri. (considerando que a rota é estática durante o tráfego do fluxo)

 * Implementar a garantia de QoS -- monitar? ....

 * Implementar o servidor third-party que vai coordenar o QoS as a service. -- todos os controladores da rota precisam informar que fazem da rota e que estao fornecendo qos pra o fluxo devidamente identificado com um identificador unico.  

 * Aplicacao no host informando QoS dos seus fluxos

 * Suporte a redes virtuais --- por último....

## Ordem de desenvolvimento{

* --- Algumas coisas já são existentes só colocar para ficar mais funcional

*  #Resolver a parte de configuracao manual

* #Implementar DHCPv4 e v6

* #Resolver a parte básica de roteamento.... (descoberta de topologia)

* #Resolver a parte de suporte a IPv6.

* #Resolver a parte de classificacao

* #Resolver a parte de garantia de QoS.

* #Resolver a parte de monitoramento de QoS.

* #Resolver a parte de QoS as a Service.

}
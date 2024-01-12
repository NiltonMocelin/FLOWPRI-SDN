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
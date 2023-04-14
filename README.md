# FrameworkTCC

* Código referente ao projeto da disciplina TCC-002 - UDESC 2022

## Versão dos recursos utilizados:
- Mininet: 2.3.0b2
- OVS: 2.13.1
- Ryu: 4.34
- Python: 3.8.5
- Linux & Kernel: (Ubuntu 20.04.1 LTS) 5.4.0-42-generic



# ATUALIZAÇÕES

### Objetivos

- Arrumar a parte de endereçamentos - remover a parte de traduções de endereços

- Automatizar a configuração de switches no domínio

- Abrir uma porta para tornar o controlador programável

- Receber arquivos de configuração de largura de banda de portas dos switches

- Receber arquivos de configuração de rotas (prefixos aceitos e bloqueados de cada switch)

- Detectar modificações nos switches (criação/remoção de portas)

- Implementar OSPF para identificar rotas

- Implementar um grafo da rede e identificar rotas juntamente com o OSPF

- Containerizar o controlador FLOWPRI

- Modificar o contrato para suportar dst_port e protocolo (TCP/UDP)

- Adaptar suporte a NAT

- Melhorar a disseminação de contratos de QoS

- Implementar RollBack de QoS

- Implementar classificação de tráfego e descoberta de requisitos de QoS

- Implementar mecanismo de priorização (buscar outra abordagem)


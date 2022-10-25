#teste de emprestimo
#verificar se a primeira regra eh removida corretamente para alocar a ultima, uma vez que nao eh possivel emprestar
sh switchQueueConf2.sh
python contrato_cli_v2.py 10.10.10.1 172.16.10.1 172.16.10.2 1000 1 1
python contrato_cli_v2.py 10.10.10.1 172.16.10.2 172.16.10.2 1000 1 1
python contrato_cli_v2.py 10.10.10.1 172.16.10.3 172.16.10.2 2000 1 2
python contrato_cli_v2.py 10.10.10.1 172.16.10.4 172.16.10.2 2000 2 1


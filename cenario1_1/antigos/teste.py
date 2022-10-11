import json

contratos = []

contrato = {
        "contrato":
            {
            "ip_origem":"172.16.10.1",
            "ip_destino":"172.16.10.2",
            "banda":"1000",
            "prioridade":"1",
            "classe":"1"
            }
        } 

contratos.append(json.dumps(contrato))

for i in contratos:
    print(i)
    ipsrc = json.loads(i)['contrato']['ip_origem']
    ipdst = json.loads(i)['contrato']['ip_destino']

    print('ipsrc: %s, ipdst: %s\n' % (ipsrc, ipdst))

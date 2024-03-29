#avoid circular import https://builtin.com/articles/python-circular-import

import socket
from fp_constants import IPC, PORTAC_C, MACC, PORTAC_H, PORTAC_X, CRIAR, CPT
from fp_constants import contratos

from fp_switch import SwitchOVS
from fp_contrato import Contrato

# try:
# from main_controller import delContratoERegras, tratador_regras, send_icmpv4, tratador_addSwitch, tratador_rotas
# except ImportError:
#     print('erro de importacao aa')
    
import json, struct, time, datetime

#servidor para escutar hosts
def servidor_socket_hosts():

    # from main_controller import send_icmpv4, delContratoERegras
    print("Iniciando servidor de contratos para hosts....\n")

    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#um desses funfa
    tcp.bind((IPC, PORTAC_H))
#    tcp.bind(("127.0.1.1", 4444))
#    tcp.bind((socket.gethostbyname(socket.gethostname()),4444))

    #print("host:{0} Ouvindo em {1}".format(socket.gethostname(),socket.gethostbyname(socket.gethostname())))

    tcp.listen(5)

    while True:
        conn, addr = tcp.accept()

        tempo_i = round(time.monotonic()*1000)
        print("[%s] servidor_socket host - recebendo contrato:\n" % (datetime.datetime.now().time()))
        
        #print]("[host]Conectado: ")
        #print](addr)
        #print]("\n")

        data = conn.recv(4)
        qtdBytes = struct.unpack('<i',data)[0]

        data = conn.recv(qtdBytes)

        #recebeu um contrato fecha a conexao, se o host quiser enviar mais, que inicie outra
        conn.close()
        
        #print](data)
        contratos = json.loads(data.encode('utf-8'))

        for contrato in contratos['contratos']:

            #criar as regras de marcacao e encaminhamento nos switches da entre ip_src e ip_dst
            #enviar um icmp 15 ja perguntando se existem controladores interessados em receber o contrato
            #pegar os dados do contrato
            cip_src = contrato['ip_src']
            cip_dst = contrato['ip_dst']

            cip_dport = contrato['dst_port']
            cip_sport = contrato['src_port']
            cip_proto = contrato['ip_proto']

            cip_ver = contrato['ip_ver']

            banda = contrato['banda']
            prioridade =  contrato['prioridade']
            classe =  contrato['classe']

            contrato_obj = Contrato(cip_ver, cip_src, cip_dst, cip_sport, cip_dport, cip_proto, CPT[(classe, prioridade, banda)], classe, prioridade, banda)

            #### OBS -- Implementar : garantir que exista apenas um contrato com match para ip_src, ip_dst - e mais campos se forem usar - que se outro contrato vier com esse match, substituir o que ja existe 
            #OBS - os contratos sao armazenados como string, entao para acessa-los como json, eh preciso carregar como json: json.loads(contrato)['contrato']['ip_origem']
            #pegar os switches da rota
            switches_rota = SwitchOVS.getRota(None, cip_dst)

            if switches_rota == None:
                print("[%s] Rota nao encontrada entre src:%s dst:%s dport:%s\nRegras nao criadas - ICMP nao enviado" % (datetime.datetime.now().time(), cip_src, cip_dst,cip_dport))
                print("[%s] servidor_socket host - fim:\n" % (datetime.datetime.now().time()))

            #deletando o contrato anterior e as regras a ele associadas
            delContratoERegras(switches_rota=switches_rota, contrato = contrato_obj)
    
            #print]("contrato salvo \n")
            contratos.append(contrato_obj)      

            print("[%s] servidor_socket host - contrato recebido:\n" % (datetime.datetime.now().time()))
            print(contrato_obj.toString())

            #pegando as acoes do alocarGBAM
            acoes = []

            #em todos os switches da rota - criar regras de encaminhamento
            #nao precisa injetar o pacote,pois era um contrato para este controlador
            for s in switches_rota:
                out_port = s.getPortaSaida(cip_dst)
                acoes_aux = s.alocarGBAM(ip_ver=cip_ver, porta_saida=out_port, ip_src=cip_src,ip_dst= cip_dst,proto= cip_proto, src_port= cip_sport, dst_port=cip_dport, banda= banda, prioridade = prioridade, classe=classe)

                #retorno vazio = nao tem espaco para alocar o fluxo
                if len(acoes_aux)==0:
                    #rejeitar o fluxo
                    #print]("Fluxo rejeitado!\n")
                    break
                
                #adicionando as acoes
                for a in acoes_aux:
                    acoes.append(a)

            #retorno vazio = nao tem espaco para alocar o fluxo
            if len(acoes_aux)==0:
                #rejeitar o fluxo
                continue

            #chegou ate aqui, entao todos os switches possuem espaco para alocar o fluxo
            #executar cada acao de criar/remover regras\
            #print]("Executar acoes: \n")
            for a in acoes:
                a.executar()

            #verificar as regras alocadas
            for s in switches_rota:
                s.listarRegras()

            #1 criar regra de marcacao/classificacao - switch mais da borda = que disparou o packet_in
            #encontrar qual tos foi definido para a criacao da regra no switch de borda mais proximo do emissor
            #pq pegar o tos da regra definida na acao e nao o tos baseado na classe, prioridade e banda do
            # contrato? - pq a regra pode estar emprestando banda, nesse caso, a classe esta diferente da original, e consequentemente o tos tbm esta

            for a in acoes:
                if(a.nome_switch == switches_rota[0].nome and a.codigo == CRIAR):
                    #criando a regra de marcacao - switch mais da borda emissora

                    ############### aqui ##########
                    switches_rota[0].addRegraC(cip_src, cip_dst, cip_proto, cip_dport, a.regra.tos)
                    break

            #enviando o icmp 15 ---- obs nao posso enviar o icmp 15, pois o controlador nao  conhece o end MAC do destino
            # o melhor jeito seria inserir isso no contrato PENSAR
            # como o endereco mac nao importa nesses switches l2 e a ideia eh que o pacote seja aproveitado pelos controladores da rota e nao do host final
            # o host final deve descartar ou ignorar esse pacote
            # assim, eh possivel 'inventar' um endereco MAC e rotear apenas com o endereco IP
            #deve ser enviado pelo switch mais proximo do destino (da borda) - se nao cada switch vai precisar tratar esse pacote
            switch_ultimo = switches_rota[-1]
            switch_ultimo_dp = switch_ultimo.getDP()
            out_port = switch_ultimo.getPortaSaida(cip_dst)

            #print]("Porta SAIDA: %d\n" % (out_port))

            #enviar os identificadores do contrato (v2: ip origem/destino sao os identificadores - origem vai em dados, destino vai no destino do icmp ) 
            data = {"ip_src":cip_src}
            data = json.dumps(data)

            send_icmpv4(switch_ultimo_dp, MACC, IPC, MACC, cip_dst, out_port, 0, data, 1, 15,64)        

            # logging.info('[server-host] fim - tempo: %d\n' % (round(time.monotonic()*1000) - tempo_i))        

            print("[%s] servidor_socket host - fim:\n" % (datetime.datetime.now().time()))

#servidor para escutar controladores - mesmo que o de hosts, mas o controlador que recebe um contrato nao gera um icmp inf. req.
def servidor_socket_controladores():

    from main_controller import delContratoERegras

    print("Iniciando servidor de contratos entre controladores....\n")

    #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#um desses funfa
    tcp.bind((IPC, PORTAC_C))
#    tcp.bind(("127.0.1.1", 4444))
#    tcp.bind((socket.gethostbyname(socket.gethostname()),4444))

    #print]("Controlador:{0} Ouvindo em {1}".format(socket.gethostname(),socket.gethostbyname(socket.gethostname())))

    tcp.listen(5)

    while True:
        conn, addr = tcp.accept()

        print("[%s] servidor_socket controlador - recebendo contrato:\n" % (datetime.datetime.now().time()))
        tempo_i = round(time.monotonic()*1000)
        
        #print]("[controlador]Conectado: ")
        #print](addr)
        #print]("\n")

        #primeiro: receber quantos contratos serao enviados para cah - inteiro de 4 bytes
        data = conn.recv(4)
        qtdContratos = struct.unpack('<i',data)[0]

        #para cada contrato, receber qtd de bytes (outro inteiro de 4 bytes) e entao receber esses bytes
        for i in range(qtdContratos):
            data = conn.recv(4)
            qtdBytes = struct.unpack('<i',data)[0]

            data = conn.recv(qtdBytes)
            #print](data)
            #contrato = json.loads(data.encode('utf-8'))
            #JSON LOADS CARREGA COMO UNICODE essa porcaria
            #contrato = data.decode("utf-8")
            contrato = json.loads(data.encode('utf-8'))

#### OBS -- Implementar : garantir que exista apenas um contrato com match para ip_src, ip_dst - e mais campos se forem usar - que se outro contrato vier com esse match, substituir o que ja existe 
#OBS - os contratos sao armazenados como string, entao para acessa-los como json, eh preciso carregar como json: json.loads(contrato)['contrato']['ip_origem']

                   #criar as regras de marcacao e encaminhamento nos switches da entre ip_src e ip_dst
#enviar um icmp 15 ja perguntando se existem controladores interessados em receber o contrato
        #pegar os dados do contrato - manda um por vez
            cip_src = contrato['ip_src']
            cip_dst = contrato['ip_dst']

            cip_sport = contrato['src_port']
            cip_dport = contrato['dst_port']
            cip_proto = contrato['ip_proto']

            cip_ver = contrato['ip_ver']

            banda = contrato['banda']
            prioridade =  contrato['prioridade']
            classe =  contrato['classe']

            contrato_obj = Contrato(cip_ver, cip_src, cip_dst, cip_sport, cip_dport, cip_proto, CPT[(classe, prioridade, banda)], classe, prioridade, banda)

            #pegando os switches da rota
            switches_rota = SwitchOVS.getRota(None, cip_dst)

            if switches_rota == None:
                print("[%s] Rota nao encontrada entre src:%s dst:%s \nRegras nao criadas - ICMP nao enviado" % (datetime.datetime.now().time(), cip_src, cip_dst))
                print("[%s] servidor_socket host - fim:\n" % (datetime.datetime.now().time()))
                conn.close()

            #deletando o contrato anterior e as regras a ele associadas
            delContratoERegras(switches_rota=switches_rota, contrato=contrato_obj)

            #print]("contrato salvo \n")
            contratos.append(contrato_obj)

            print("[%s] servidor_socket controlador - contrato recebido:\n" % (datetime.datetime.now().time()))
            print(contrato_obj.toString())

            #pegando as acoes do alocarGBAM
            acoes = []

            #em todos os switches da rota - criar regras de encaminhamento
            #nao precisa injetar o pacote,pois era um contrato para este controlador
            for s in switches_rota:
                out_port = s.getPortaSaida(cip_dst)
                acoes_aux = s.alocarGBAM(ip_ver = cip_ver, ip_src= cip_src, ip_dst = cip_dst, src_port = cip_sport, dst_port = cip_dport, proto = cip_proto, porta_saida = out_port, banda = banda, prioridade=prioridade, classe = classe)

                #retorno vazio = nao tem espaco para alocar o fluxo
                if len(acoes_aux)==0:
                    #rejeitar o fluxo
                    #print]("Fluxo rejeitado!\n")
                    break

                #adicionando as acoes
                for a in acoes_aux:
                    acoes.append(a)

            #retorno vazio = nao tem espaco para alocar o fluxo
            #
            if len(acoes_aux)==0:
                    #fluxo rejeitado
                continue
            
            #chegou ate aqui, entao todos os switches possuem espaco para alocar o fluxo
            #executar cada acao de criar/remover regras
            for a in acoes:
                a.executar()

            #1 criar regra de marcacao/classificacao - switch mais da borda = que disparou o packet_in
            #encontrar qual tos foi definido para a criacao da regra no switch de borda mais proximo do emissor
            #pq pegar o tos da regra definida na acao e nao o tos baseado na classe, prioridade e banda do
            # contrato? - pq a regra pode estar emprestando banda, nesse caso, a classe esta diferente da original, e consequentemente o tos tbm esta
            
            for a in acoes:
                if(a.nome_switch == switches_rota[0].nome and a.codigo == CRIAR):
                    #criando a regra de marcacao - switch mais da borda emissora
                    switches_rota[0].addRegraC(ip_ver = cip_ver, ip_src=cip_src, ip_dst= cip_dst, src_port = cip_sport, dst_port=cip_dport, proto = cip_proto, ip_dscp =a.regra.tos)
                    break

            #Nao enviar um icmp 15, pois o protocolo atual eh que todos respondam o icmp 15 do primeiro controlador
        #fechar a conexao e aguardar nova
            # logging.info('[server-control] fim - tempo: %d\n' % (round(time.monotonic()*1000) - tempo_i))

        conn.close()
        print("[%s] servidor_socket controlador - fim:\n" % (datetime.datetime.now().time()))
  



def tratador_configuracoes():
    from main_controller import tratador_regras, tratador_addSwitch, tratador_rotas
    print("Iniciando o tratador de arquivos de config....\n")

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    #um desses funfa
    tcp.bind((IPC, PORTAC_X))

    tcp.listen(5)

    while True:
        conn, addr = tcp.accept()

        #receber a qtd de bytes do json a ser recebido
        data = conn.recv(4)

        qtdBytes = struct.unpack('<i',data)[0]
        print("qtdBytes {}".format(qtdBytes))

        data = conn.recv(qtdBytes)

        #formatando o cfg recebido
        cfg = json.loads(data)

        #descobrir qual o tipo de operacao da configuracao
        #realizar as operacoes modificando os switches
        if "addswitch" in cfg:
            tratador_addSwitch(cfg['addswitch'])
        
        if "delswitch" in cfg:
            tratador_addSwitch(cfg['delswitch'])
            
        if "addrota" in cfg:
            tratador_rotas(cfg['rotas'])
        
        if "addregra" in cfg:
            tratador_regras(cfg['regras'])

        #printando o json recebido
        print(cfg)

        #fechando a conexao
        conn.close()

    return

##aqui
def enviar_contratos(ip_ver, ip_dst, dst_port, contrato_obj):
    #print]("[enviar-contratos] p/ ip_dst: %s, port_dst: %s" %(host_ip, host_port))
    tempo_i = round(time.monotonic()*1000)
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.connect((ip_dst, dst_port))
 
    print("[%s] enviar contrato p/ %s\n" % (datetime.datetime.now().time(), ip_dst))

    #teste envio [ok]
    #tcp.connect(("10.123.123.2", host_port))

    # contratos_contador = 0
    # #contar quantos contratos enviar
    # for i in contratos:
    #     if i.ip_dst == ip_dst_contrato:
    #         contratos_contador = contratos_contador+1
    
    #enviar apenas um contrato
    contratos_contador = 1
    
    #enviar quantos contratos serao enviados
    tcp.send(struct.pack('<i',contratos_contador))

    #para cada contrato, antes de enviar, verificar o size e enviar o size do vetor de bytes a ser enviado
    #encontrar os contratos que se referem ao ip_dst informado e enviar para o host_ip:host_port

    vetorbytes = json.dumps(contrato_obj.toJSON()).encode('utf-8')
    qtdBytes = struct.pack('<i',len(vetorbytes))
    tcp.send(qtdBytes)
    tcp.send(vetorbytes)
    print(contrato_obj.toString())

    #fechando a conexao
    #print]("\n")
    tcp.close()
    print("[%s] enviar contrato p/ %s - fim\n" % (datetime.datetime.now().time(), ip_dst))
    # logging.info('[Packet_In] icmp 16 - enviar_contrato - fim - tempo: %d\n' % (round(time.monotonic()*1000) - tempo_i))

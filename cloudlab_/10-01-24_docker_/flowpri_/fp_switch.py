
from fp_acao import Acao
from fp_porta import Porta
from fp_constants import CPT, ALL_TABLES, CRIAR, REMOVER, FORWARD_TABLE, CLASSIFICATION_TABLE
from fp_regra import Regra

from ryu.lib.packet import ether_types


class SwitchOVS:
    def __init__(self, datapath, name, controller): 
        
        print("Novo switch: nome = S%s" % (str(name)))

        self.controller = controller

        self.datapath = datapath
        self.nome = name
        self.portas = []

        #isso faz sentido?
        #Como adicionar itens a um dicionario -> dicio['idade'] = 20
        self.macs = {} #chave: mac, valor: porta
        self.redes = {} #chave: ip, valor: porta
        self.hosts= {} #chave: ip, valor: mac

        
        ####### Rotas e saltos
        ####### os vetores/dicionarios anteriores sao suficientes para definir as rotas, no entanto uma maneira mais facil eh com uma tabela especifica orientada para redes (self.redes)
        # em um dominio switches sao programados para possuirem informacoes sobre as rotas que suportam
        # uma informacao de [ip_rede + porta de saida]
        # assim, eh definida uma forma de adicionar e remover informacoes de roteamento, que eh salvo na classe do switch no controlador

        #funcoes necessarias:
        #checkBanda - para ver onde posicionar um fluxo (emprestar largura de banda se preciso)
        #addRegra
        #delRegra - deleta a regra por id
        #getRegra - pensar em um identificador para conseguir as regras
        #updateRegras - passa todas um vetor de regras vindos do switch, para atualizar o vetor da classe

    def addPorta(self, nomePorta, larguraBanda, proximoSwitch):
        print("[S%s] Nova porta: porta=%s, banda=%s, proximoSalto=%s\n" % (str(self.nome), str(nomePorta), str(larguraBanda), str(proximoSwitch)))
        #criar a porta no switch
        self.portas.append(Porta(nomePorta, larguraBanda*.33, larguraBanda*.35, 0, 0, proximoSwitch))

        #print]("\nSwitch %s criado\n" % (name))
    

    def updateRegras(self, ip_src, ip_dst, tos):
        #pega todas as regras do switch e atualiza na porta nomePorta (poderia atualizar todas as portas do switch jah)
        
#        Flow Removed Message https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html
#       Quando um fluxo expira ou eh removido no switch, este informa o controlador -- se aproveitar desse evento e atualizar as regras do switch !!!!
        #print]("\n[S%s]UpdateRegras-in\n" % (str(self.nome)))
        #debug
        self.listarRegras()
        #na verdade a del regra esta localizando a classe e prioridade por meio do tos, que seria uma tarefa desta funcao update...
        #obter a porta de saida do switch com a tabela de roteamento com base no ip da rede destino  -- que ainda nao foi implementada
        out_port = self.getPortaSaida(ip_dst)
        porta = self.getPorta(out_port)
        #if(porta.delRegra(ip_src, ip_dst, tos)>0):
        #    print("[updateRegras]regra-removida ip_src:%s, ip_dst:%s, tos:%s\n" % (ip_src,ip_dst,tos))
#
        #print("[S%s]UpdateRegras-ok-out\n" % (str(self.nome)))

        #debug
        self.listarRegras()

        return 0

    def getPorta(self, nomePorta):

        for i in self.portas:
            # %s x %s\n" % (i.nome, nomePorta))
            if str(i.nome) == str(nomePorta):
                return i
        #print("[getPorta] porta inexistente: %s\n" % (nomePorta))
        return None

    def alocarGBAM(self, nomePorta, origem, destino, proto, dport, banda, prioridade, classe):

        banda = int(banda)
        prioridade = int(prioridade)
        classe = int(classe)

        #armazenar as acoes a serem tomadas
        acoes = []

#       As regras sempre estao atualizadas, pois quando uma eh modificada, essa notifica o controlador, que chama updateRegras        
#        self.updateRegras()# atualizar as regras, pois algumas podem nao estar mais ativas = liberou espaco -- implementar

# o TOS eh decidido aqui dentro, pois dependendo do TOS, pode se definir uma banda, uma prioridade e uma classe
#a classe, a prioridade e a banda sao os atributos originais do fluxo

#funcao injetar pacote - o pacote que gera o packet in as vezes, em determinados switches, precisam ser reinjetados
#principalmente no switch que gerou o packet in ou no ultimo switch da rota
#Mas ha casos em que as regras precisam ser criadas nos switches da rota e ser injetado apenas no ultimo, assim, precisa fazer o tratamento

        porta = self.getPorta(str(nomePorta))
 
        print("[alocarGBAM-S%s] porta %s, src: %s, dst: %s, banda: %d, prioridade: %d, classe: %d \n" % (self.nome, str(nomePorta), origem, destino,banda, prioridade, classe))

        #caso seja classe de controle ou best-effort, nao tem BAM, mas precisa criar regras da mesma forma
        #best-effort
        if classe == 3:
            self.addRegraF(origem,destino, 60, nomePorta, 6,None,0, hardtime=10)
            
            return acoes

        #controle
        if classe == 4:
            self.addRegraF(origem,destino, 61, nomePorta, 7,None,0)
            
            return acoes

        #para generalizar o metodo GBAM e nao ter de repetir codigo testando para uma classe e depois para outra
        outraClasse = 1
        if classe == 1:
            outraClasse=2

        #banda usada e total na classe original
        cU, cT = Porta.getUT(porta, classe)

        # print("[antes de alocar] banda usada: %d, banda total: %d \n" % ( cU, cT)) 

        ### antes de alocar o novo fluxo, verificar se ja nao existe uma regra para este fluxo -- caso exista remover e adicionar de novo? ou so nao alocar?
        #a principio - remover e alocar de novo
        tos = CPT[(str(classe), str(prioridade), str(banda))] 
        
        #de qual classe a regra foi removida? classe 1, classe 2, ou -1 regra nao removida
        classe_removida = porta.delRegra(origem, destino, tos)
        if(classe_removida>0):
            tos_aux = CPT[(str(classe_removida), str(prioridade), str(banda))] 
            self.delRegraT(origem, destino, int(tos_aux), ALL_TABLES)
            print("[S%s]regra removida - ip_src:%s, ip_dst:%s, tos:%s\n" % (self.nome,origem,destino,tos_aux))
        #pronto, nao vai existir regra duplicada - pode alocar

        #testando na classe original
        if int(banda) <= cT - cU: #Total - usado > banda necessaria
            #criar a regra com o TOS = (banda + classe)
            #regra: origem, destino, TOS ?
            tos = CPT[(str(classe), str(prioridade), str(banda))] #obter do vetor CPT - sei a classe a prioridade e a banda = tos

            #nova acao: criar regra: ip_src: origem, ip_dst: destino, porta de saida: nomePorta, tos: tos, banda:banda, prioridade:prioridade, classe:classe, emprestando: nao
            acoes.append( Acao(self.controller.getSwitchByName(self.nome), nomePorta, CRIAR, Regra(origem,destino,nomePorta,tos,banda,prioridade,classe,0)))   

            return acoes #retornando as acoes

        else: #nao ha banda suficiente 
            #verificar se existe fluxo emprestando largura = verificar se alguma regra nas filas da classe esta emprestando banda
            emprestando = []
            bandaE = 0

            #sim: somar os fluxos que estao emprestando e ver se a banda eh suficiente para alocar este fluxo 

            for i in Porta.getRules(porta, classe, 1):
                if i.emprestando == 1:
                    emprestando.append(i)

            for i in Porta.getRules(porta, classe, 2):
                if i.emprestando ==1:
                    emprestando.append(i)

            for i in Porta.getRules(porta, classe, 3):
                if i.emprestando ==1:
                    emprestando.append(i)

            contadorE = 0
            for i in emprestando:
                bandaE += int(i.banda)
                contadorE+=1

                if cT - cU + bandaE >= int(banda):
                    break
            
            #se as regras que estao emprestando representam largura de banda suficiente para que removendo-as, posso alocar o novo fluxo, entao:
            if cT - cU + bandaE >= int(banda):
                for i in range(contadorE): #criando as acoes para remover as regras que estao emprestando
                    acoes.append( Acao(self.controller.getSwitchByName(self.nome), nomePorta, REMOVER, Regra(emprestando[i].ip_src,emprestando[i].ip_dst,nomePorta,emprestando[i].tos,emprestando[i].banda,emprestando[i].prioridade,emprestando[i].classe,emprestando[i].emprestando)))   
                
                tos = CPT[(str(classe), str(prioridade), str(banda))] #obter do vetor CPT - sei a classe a prioridade e a banda = tos
                
                #criando a acao  para criar a regra do fluxo, depois de remover as regras selecionadas que emprestam.
                acoes.append( Acao(self.controller.getSwitchByName(self.nome), nomePorta, CRIAR, Regra(origem,destino,nomePorta,tos,banda,prioridade,classe,0)))   
                return acoes
                
            else:       #nao: testa o nao
                #nao: ver se na outra classe existe espaco para o fluxo
                #remover os fluxos que foram adicionados em emprestando
                #emprestando.clear()

                #banda usada e total na outra classe
                cOU, cOT = Porta.getUT(porta, outraClasse)
                if int(banda) <= cOT - cOU:

                    #calcular o tos - neste switch o fluxo o tos permanece o mesmo, a regra eh criada no vetor da classe que empresta mas no switch deve ser criada na classe original - isso pode pois todas as filas compartilham da mesma banda e sao limitadas com o controlador
                    tos = CPT[(str(classe), str(prioridade), str(banda))] #novo tos equivalente
                    
                    #sim: alocar este fluxo - emprestando = 1 na classe em que empresta - na fila correspondente
                    acoes.append( Acao(self.controller.getSwitchByName(self.nome), nomePorta, CRIAR, Regra(origem,destino,nomePorta,tos,banda,prioridade,outraClasse,1)))   
                    
                    return acoes

                else:
                        #nao: verificar na classe original se nao existem fluxos de menor prioridade que somados dao minha banda
                        
                    bandaP = 0
                    remover = []

                    #sim: remove eles e aloca este
                    if prioridade > 1:
    
                        for i in Porta.getRules(porta, classe, 1):
                            bandaP += int(i.banda)
                            remover.append(i)

                            if cT - cU + bandaP >= int(banda):
                                break
                        
                    if prioridade > 2:
                        if cT - cU + bandaP < int(banda):
                            for i in Porta.getRules(porta, classe, 2):
                                bandaP += int(i.banda)
                                remover.append(i)

                                if cT - cU + bandaP >= int(banda):
                                    break

                    if cT - cU + bandaP >= int(banda):
                        for i in remover:
                            acoes.append( Acao(self.controller.getSwitchByName(self.nome), nomePorta, REMOVER, Regra(i.ip_src,i.ip_dst,nomePorta,i.tos,i.banda,i.prioridade,i.classe,i.emprestando)))   
                
                        #adiciona na classe original
                        tos = CPT[(str(classe), str(prioridade), str(banda))] #obter do vetor CPT - sei a classe a prioridade e a banda = tos
                        
                        acoes.append( Acao(self.controller.getSwitchByName(self.nome), nomePorta, CRIAR, Regra(origem,destino,nomePorta,tos,banda,prioridade,classe,0)))   
                        
                        return acoes

                    else:

                        #nao: rejeita o fluxo - criando uma regra de drop por uns 5segundos
                        print("[alocaGBMA]fluxo descartado\n")
                        #FAZER NADA - se nao tiver regra, o pacote eh dropado automaticamente.
                        return acoes

        #algum erro ocorreu 
        return acoes


    #criar uma mensagem para remover uma regra de fluxo no ovsswitch
    def delRegraT(self, ip_src, ip_dst, tos, tabela=ALL_TABLES):

        #tabela = 255 = ofproto.OFPTT_ALL = todas as tabelas
        #print("Deletando regra - ipsrc: %s, ipdst: %s, tos: %d, tabela: %d\n" % (ip_src, ip_dst, tos, tabela))
        #tendo o datapath eh possivel criar pacotes de comando para o switch/datapath
        #caso precise simplificar, pode chamar o cmd e fazer tudo via ovs-ofctl

        #modelo com ovs-ofctl:
        #we can remove all or individual flows from the switch
        # sudo ovs-ofctl del-flows <expression>
        # ex. sudo ovs-ofctl del-flows dp0 dl_type=0x800
        # ex. sudo ovs-ofctl del-flows dp0 in_port=1
        datapath = self.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #remover a regra meter associada
        meter_id = int(ip_src.split(".")[3] + ip_dst.split(".")[3])                
        self.delRegraM(meter_id)

        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=ip_src, ipv4_dst=ip_dst, ip_dscp=tos)
        #match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_dst=ip_dst) #, ip_dscp=20)
        #match = parser.OFPMatch()
        #mod = datapath.ofproto_parser.OFPFlowMod(datapath, table_id=tabela, command=ofproto.OFPFC_DELETE,  match=match)
        
        #funcionam
        # mod = datapath.ofproto_parser.OFPFlowMod(datapath, command=ofproto.OFPFC_DELETE, out_port=ofproto.OFPP_ANY, match=match)
        # mod = datapath.ofproto_parser.OFPFlowMod(datapath, command=ofproto.OFPFC_DELETE, match=match, table_id=ofproto.OFPTT_ALL, out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY)
        mod = datapath.ofproto_parser.OFPFlowMod(datapath, command=ofproto.OFPFC_DELETE, match=match, table_id=tabela, out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY)

        ##esse funciona - remove tudo
        #mod = datapath.ofproto_parser.OFPFlowMod(datapath, command=ofproto.OFPFC_DELETE, table_id=ofproto.OFPTT_ALL, out_port=ofproto.OFPP_ANY, out_group=ofproto.OFPG_ANY)
        
        ##print("deletando regra\n")
        ##print(mod)
        ##print("\n")
        datapath.send_msg(mod)

        return 0

#Injetar pacote no controlador com instrucoes - serve para injetar pacotes que foram encaminhado por packet_in (se nao eles sao perdidos)
    def injetarPacote(self, datapath, fila, out_port, package):
        actions = [datapath.ofproto_parser.OFPActionSetQueue(fila), datapath.ofproto_parser.OFPActionOutput(out_port)] 
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=datapath.ofproto.OFP_NO_BUFFER,
            in_port=100,
            actions=actions,
            data=package.data)
        #print("[Pacote-Injetado]: ")
        #print(out)
        #print("\n")

        datapath.send_msg(out)

#add regra tabela FORWARD
    def addRegraF(self, ip_src, ip_dst, ip_dscp, out_port, fila, meter_id, flag, hardtime=None):
        #https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#flow-instruction-structures
# hardtimeout = 5 segundos # isso eh para evitar problemas com pacotes que sao marcados como best-effort por um contrato nao ter chego a tempo. Assim vou garantir que daqui 5s o controlador possa identifica-lo. PROBLEMA: fluxos geralmente nao duram 5s, mas eh uma abordagem.
        
        #Para que a regra emita um evento de flow removed, ela precisa carregar uma flag, adicionada no OFPFlowMod
        #flags=ofproto.OFPFF_SEND_FLOW_REM
        
        datapath = self.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        idletime = 30 # 0 = nao limita
        #hardtime = None

        prioridade = 100
       
        #match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ip_proto=in_proto.IPPROTO_TCP,ipv4_src=ip_src, ipv4_dst=ip_dst,ip_dscp=ip_dscp)
        
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,ipv4_src=ip_src, ipv4_dst=ip_dst)
        
        if(ip_dscp != None):
            match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP,ipv4_src=ip_src, ipv4_dst=ip_dst,ip_dscp=ip_dscp)
        
        actions = [parser.OFPActionSetQueue(fila), parser.OFPActionOutput(out_port)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)] # essa instrucao eh necessaria?
 
###nao esta funcionando 
        if meter_id != None:
            inst.append(parser.OFPInstructionMeter(meter_id=meter_id))
#            inst = [parser.OFPInstructionMeter(meter_id,ofproto.OFPIT_METER), parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        #marcar para gerar o evento FlowRemoved
        if flag == 1:
            mod = parser.OFPFlowMod(datapath=datapath, idle_timeout = idletime, priority=prioridade, match=match, instructions=inst, table_id=FORWARD_TABLE, flags=ofproto.OFPFF_SEND_FLOW_REM)
            datapath.send_msg(mod)
            return

        mod = parser.OFPFlowMod(datapath=datapath, idle_timeout = idletime, priority=prioridade, match=match, instructions=inst, table_id=FORWARD_TABLE)

        if hardtime != None:
            mod = parser.OFPFlowMod(datapath=datapath, idle_timeout = idletime, hard_timeout = hardtime, priority=prioridade, match=match, instructions=inst, table_id=FORWARD_TABLE)

        #print("[addRegraF]:")
        #print(mod)
        #print("\n")

        if(ip_dscp == None):
            ip_dscp = 0
        #printar a regra criada
        #if meter_id != None:
        #    print("[addRegraF-S%s]: src:%s, dst:%s, dscp:%d, porta:%s, fila: %d, meter:%d, flag:%d\n" % (self.nome, ip_src, ip_dst, ip_dscp, out_port, fila, meter_id, flag))
        #else:
        #    print("[addRegraF-S%s]: src:%s, dst:%s, dscp:%d, porta:%s, fila: %d, flag:%d\n" % (self.nome, ip_src, ip_dst, ip_dscp, out_port, fila, flag))

        datapath.send_msg(mod)
        
#add regra tabela CLASSIFICATION
#se o destino for um ip de controlador, 
    def addRegraC(self, ip_src, ip_dst, ip_dscp):
        #https://ryu.readthedocs.io/en/latest/ofproto_v1_3_ref.html#flow-instruction-structures
         #criar regra na tabela de marcacao - obs - utilizar idletime para que a regra suma - serve para que em switches que nao sao de borda essa regra nao exista
                         #obs: cada switch passa por um processo de enviar um packet_in para o controlador quando um fluxo novo chega,assim, com o mecanismo de GBAM, pode ser que pacotes de determinados fluxos sejam marcados com TOS diferentes da classe original, devido ao emprestimo, assim, em cada switch o pacote pode ter uma marcacao - mas com essa regra abaixo, os switches que possuem marcacao diferentes vao manter a regra de remarcacao. Caso ela expire e cheguem novos pacotes, ocorrera novo packet in e o controlador ira executar um novo GBAM - que vai criar uma nova regra de marcacao
        #print("[criando-regra-tabela-marcacao] ipsrc: %s, ipdst: %s, tos: %d\n" % (ip_src, ip_dst, ip_dscp))

        datapath = self.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        
#        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ip_proto=in_proto.IPPROTO_TCP, ipv4_src=ip_src, ipv4_dst=ip_dst)
        
        match = parser.OFPMatch(eth_type=ether_types.ETH_TYPE_IP, ipv4_src=ip_src, ipv4_dst=ip_dst)
        actions = [parser.OFPActionSetField(ip_dscp=ip_dscp)]

        inst = [parser.OFPInstructionGotoTable(FORWARD_TABLE), parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        idletime = 30 # 30s sem pacotes, some
        prioridade = 100

        mod = parser.OFPFlowMod(datapath=datapath, idle_timeout = idletime, priority=prioridade, match=match, instructions=inst, table_id=CLASSIFICATION_TABLE)
        datapath.send_msg(mod)

    #criando regra meter
    def addRegraM(self, meter_id, banda):
        datapath = self.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        #criando meter bands
        bands = [parser.OFPMeterBandDrop(type_=ofproto.OFPMBT_DROP, len_=0, rate=banda, burst_size=10)]#e esse burst_size ajustar?
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_ADD, flags=ofproto.OFPMF_KBPS, meter_id=meter_id, bands=bands)
        datapath.send_msg(req)
        return

    def delRegraM(self, meter_id):
        datapath = self.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        req = parser.OFPMeterMod(datapath=datapath, command=ofproto.OFPMC_DELETE, meter_id=meter_id)
        datapath.send_msg(req)
        return

#adicionar rotas no switch - por agora fica com o nome de rede
    def addRede(self, ip_dst, porta): 
        print("[S%s]Rede adicionada %s: %s" % (self.nome, ip_dst, str(porta)))
        self.redes[ip_dst]=porta
        return

    def addMac(self, mac, porta):
        self.macs[mac]=porta
        return

        #retorna uma porta ou -1
    def conheceMac(self, mac):
        if mac in self.macs:
            return self.macs[mac]
        
        return -1

    def addHost(self, ip, porta):
        self.hosts[ip]=porta
        return

#aqui verificar os prefixos
    def getPortaSaida(self, ip_dst):
        #retorna int

        if ip_dst in self.redes:
            return self.redes[ip_dst]

        return None

    def delRede(self, ip_dst, porta):
        #print("[%s]Rede deletada %s: %s" % (self.nome, ip_dst, porta))
        return

    def getPortas(self):
        return self.portas
    
    def getDP(self):
        return self.datapath
    

    def listarRegras(self):
        for porta1 in self.getPortas():
            # return
            print("\n[s%s-p%s] listar regras || C1T:%d, C1U:%d || C2T:%d, C2U: %d ||:\n" % (self.nome,porta1.nome, porta1.c1T, porta1.c1U, porta1.c2T, porta1.c2U))
            for rp1c1 in porta1.p1c1rules:
                print(rp1c1.toString()+"\n")
            #print("\n -- C1P2 (qtdregras: %d):" % (este_switch.p2c1rules.length))
            for rp2c1 in porta1.p2c1rules:
                print(rp2c1.toString()+"\n")
            #print("\n -- C1P3 (qtdregras: %d):" % (este_switch.p3c1rules.length))
            for rp3c1 in porta1.p3c1rules:
                print(rp3c1.toString()+"\n")
            #print(" -- C2P1 (qtdregras: %d):" % (este_switch.p1c2rules.length))
            for rp1c2 in porta1.p1c2rules:
                print(rp1c2.toString()+"\n")
            #print("\n -- C2P2 (qtdregras: %d):" % (este_switch.p2c2rules.length))
            for rp2c2 in porta1.p2c2rules:
                print(rp2c2.toString()+"\n")
            #print("\n -- C2P3 (qtdregras: %d):" % (este_switch.p3c2rules.length))
            for rp3c2 in porta1.p3c2rules:
                print(rp3c2.toString()+"\n")


from fp_regra import Regra
from fp_constants import CPT

class Porta:
    def __init__(self, name :str , bandaC1T : int, bandaC2T : int, tamanhoFilaC1, tamanhoFilaC2, proximoSwitch : str):
        #criar filas e setar quantidade de banda para cada classe

        #tamanhoFila = quanto alem da banda posso alocar/emprestar

        #cada fila deve ter uma variavel de controle de largura de banda utilizada e uma variavel de largura de banda total
        self.nome = name
        #a principio o compartilhamento de largura de banda ocorre apenas entre essas duas classes
        #criar os vetores fila da classe 1
        self.c1T = bandaC1T #banda total para esta classe
        self.c1U = 0 #banda utilizada para esta classe
        #fila baixa prioridade 1, classe 1 (tempo real)
        self.p1c1rules = []
        #fila media prioridade 2, classe 1 (tempo real)
        self.p2c1rules = []
        #fila alta prioridade 3, classe 1 (tempo real)
        self.p3c1rules = []

        #criar os vetores fila da classe 2
        self.c2T = bandaC2T
        self.c2U = 0
        #fila baixa prioridade 1, classe 2 (dados)
        self.p1c2rules = []
        #fila media prioridade 2, classe 2 (dados)
        self.p2c2rules = []
        #fila alta prioridade 3, classe 2 (dados)
        self.p3c2rules = []

        #id do proximo switch (conectado ao link)
        self.next = proximoSwitch
        #nao eh preciso armazenar informacoes sobre as filas de best-effort e controle de rede

    def addRegra(self, ip_src, ip_dst, src_port, dst_port, proto, porta_saida, banda, prioridade, classe, tos, emprestando): #porta = nome da porta
#adicionar regra na fila correta da classe switch no controlador

        if classe == 1:
            self.c1U += int(banda)

            if prioridade == 1:             
                self.p1c1rules.append(Regra(ip_src, ip_dst, src_port, dst_port, proto, porta_saida, tos, banda, prioridade, classe, emprestando))
            elif prioridade ==2:
                self.p2c1rules.append(Regra(ip_src, ip_dst, src_port, dst_port, proto, porta_saida, tos, banda, prioridade, classe, emprestando))
            else: #prioridade ==3
                self.p3c1rules.append(Regra(ip_src, ip_dst, src_port, dst_port, proto, porta_saida, tos, banda, prioridade, classe, emprestando))
        else: #classe ==2
            self.c2U += int(banda)

            if prioridade == 1:
                self.p1c2rules.append(Regra(ip_src, ip_dst, src_port, dst_port, proto, porta_saida, tos, banda, prioridade, classe, emprestando))
            elif prioridade ==2:
                self.p2c2rules.append(Regra(ip_src, ip_dst, src_port, dst_port, proto, porta_saida, tos, banda, prioridade, classe, emprestando))
            else: #prioridade ==3
                self.p3c2rules.append(Regra(ip_src, ip_dst, src_port, dst_port, proto, porta_saida, tos, banda, prioridade, classe, emprestando))

        return 0

    
    def delRegra(self, ip_ver:str, ip_src: str, ip_dst: str, src_port: str, dst_port: str, proto: str, tos):
        #retorna 1, caso a regra tenha sido removida na classe 1, e 2 caso tenha sido removida na classe 2
        #print]("[delRegra] porta: %s, src:%s, dst:%s, tos: %d\n" % (self.nome, ip_src, ip_dst, int(tos)))
        #tos eh inteiro no dict
        tos = int(tos)

        #busca e remove a regra seja onde estiver - eh dito que nao deve existir duas regras iguais em nenhum lugar ....
        #regras podem estar na classe original, com uma prioridade, ou emprestando (na outra classe, com a mesma prioridade)

        #acho a tupla chave que representa o valor (tos) -- ou seja, acho a (classe,prioridade,banda)==tos
        keys = [k for k, v in CPT.items() if v == tos]

        #transformar a tupla em lista para poder acessar
        tuplaL = [item for t in keys for item in t] 

        #classe = tuplaL[0]

        prioridade = int(tuplaL[1])
        #banda = [2]

        #como as regras podem emprestar, elas sao armazenadas com o tos original, mas na classe em que emprestam 
        #assim, para cada prioridade, testar as duas classes

        #como pode ter um tos para prioridade 1, e outro tos para prioridade 2, nao posso usar
        
        if prioridade == 1:
            for i in self.p1c1rules:
                if i.ip_src == ip_src and i.ip_dst == ip_dst and i.src_port == src_port and i.dst_port == dst_port and i.proto == proto: #and i.tos == tos:
                    self.c1U -= int(i.banda)
                    self.p1c1rules.remove(i)
                    return 1 #tos da classe 1, prioridade 1

            for i in self.p1c2rules:
                if i.ip_src == ip_src and i.ip_dst == ip_dst and i.src_port == src_port and i.dst_port == dst_port and i.proto == proto:
                    self.c2U -= int(i.banda)
                    self.p1c2rules.remove(i)
                    return 2 #tos da classe 2, prioridade 1

        elif prioridade == 2:
            for i in self.p2c1rules:
                if i.ip_src == ip_src and i.ip_dst == ip_dst and i.src_port == src_port and i.dst_port == dst_port and i.proto == proto:
                    self.c1U -= int(i.banda)
                    self.p2c1rules.remove(i)
                    return 1

            for i in self.p2c2rules:
                if i.ip_src == ip_src and i.ip_dst == ip_dst and i.src_port == src_port and i.dst_port == dst_port and i.proto == proto:
                    self.c2U -= int(i.banda)
                    self.p2c2rules.remove(i)
                    return 2

        else: #prioridade ==3
            for i in self.p3c1rules:
                if i.ip_src == ip_src and i.ip_dst == ip_dst and i.src_port == src_port and i.dst_port == dst_port and i.proto == proto:
                    self.c1U -= int(i.banda)
                    self.p3c1rules.remove(i)
                    return 1

            for i in self.p3c2rules:
                if i.ip_src == ip_src and i.ip_dst == ip_dst and i.src_port == src_port and i.dst_port == dst_port and i.proto == proto:
                    self.c2U -= int(i.banda)
                    self.p3c2rules.remove(i)
                    return 2

        #print]("[delRegra]Regra Nao encontrada no switch-controlador\n")
        return -1 #regra nao encontrada

    @staticmethod
    def getRules(porta,classe,prioridade):#dado uma porta, classe, prioridade, retornar o vetor ex: p1c1Rules 
     
        if classe == 1:
            if prioridade == 1:
                return porta.p1c1rules
            elif prioridade ==2:
                return porta.p2c1rules
            else:
                return porta.p3c1rules
        else:
            if prioridade == 1:
                return porta.p1c2rules
            elif prioridade ==2:
                return porta.p2c2rules
            else:
                return porta.p3c2rules

    @staticmethod
    def getUT(porta, classe): #dado uma porta, classe, retornar o Total de banda e a banda utilizada pela classe
        if classe == 1:
            return porta.c1U,porta.c1T
        else:
            return porta.c2U,porta.c2T

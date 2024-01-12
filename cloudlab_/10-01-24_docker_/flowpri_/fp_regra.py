
class Regra:
    def __init__(self, ip_src, ip_dst, porta_dst, tos, banda, prioridade, classe, emprestando):
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.porta_dst = porta_dst
        self.tos = tos
        self.emprestando=emprestando
        self.banda = banda
        self.prioridade=prioridade
        self.classe = classe

        #print]("[criando-regra-controlador]src:%s; dst=%s; banda:%s, porta_dst=%d, tos=%s, emprestando=%d" % (self.ip_src, self.ip_dst, self.banda, self.porta_dst, self.tos, self.emprestando)) 

    def toString(self):
        return "[regra]src:%s; dst=%s; banda:%s, porta_dst=%d, tos=%s, emprestando=%d" % (self.ip_src, self.ip_dst, self.banda, self.porta_dst, self.tos, self.emprestando) 

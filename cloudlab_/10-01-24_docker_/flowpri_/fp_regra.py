
class Regra:
    def __init__(self, ip_src, ip_dst, src_port, dst_port, proto, porta_saida, tos, banda, prioridade, classe, emprestando):
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.porta_saida = porta_saida
        self.tos = tos
        self.emprestando=emprestando
        self.banda = banda
        self.prioridade=prioridade
        self.classe = classe
        self.src_port = src_port
        self.dst_port = dst_port
        self.proto = proto

        #print]("[criando-regra-controlador]src:%s; dst=%s; banda:%s, porta_dst=%d, tos=%s, emprestando=%d" % (self.ip_src, self.ip_dst, self.banda, self.porta_dst, self.tos, self.emprestando)) 

    def toString(self):
        return "[regra]ip_src:%s; ip_dst=%s; src_port=%s; dst_port=%s; proto=%s; banda:%s, porta_dst=%d, tos=%s, emprestando=%d" % (self.ip_src, self.ip_dst, self.src_port, self.dst_port, self.proto, self.banda, self.porta_dst, self.tos, self.emprestando) 

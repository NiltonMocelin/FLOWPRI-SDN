class Contrato:

    def __init__(self, id, ip_src, ip_dst, src_port, dst_port, proto, dscp, classe, prioridade, banda):
        self.id = id
        ip_src = ip_src
        ip_dst = ip_dst
        src_port = src_port
        dst_port = dst_port
        proto = proto
        dscp = dscp
        classe = classe
        prioridade = prioridade
        banda = banda
    
    def toString(self):
        print("Contrato: ip_src:%s; ip_dst:%s; src_port:%s; dst_port:%s; proto:%s; dscp:%s; classe:%s; prioridade:%s; banda:%s;")
    
    def toJSON(self):
        return ''
    
    #inicialize o init com none e passe um json para carregar o contrato
    def loadJSON(self, json):
        return True

    


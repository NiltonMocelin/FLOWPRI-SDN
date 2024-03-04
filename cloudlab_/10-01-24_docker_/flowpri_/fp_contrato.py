# import json

contador = 0

class Contrato:

    def __init__(self, ip_ver : str, ip_src: str, ip_dst: str, src_port: str, dst_port: str, proto: str, dscp:str, classe: str, prioridade: str, banda: str):
        global contador
        contador += 1
        
        self.id = contador
        self.ip_ver = ip_ver
        self.ip_src = ip_src
        self.ip_dst = ip_dst
        self.src_port = src_port
        self.dst_port = dst_port
        self.proto = proto
        self.dscp = dscp
        self.classe = classe
        self.prioridade = prioridade
        self.banda = banda
    
        #inicialize o init com none e passe um json para carregar o contrato
    def loadFromJSON(self, json_file):

        self.ip_ver = json_file["ip_ver"]
        self.proto = json_file["ip_proto"]
        self.ip_src = json_file["ip_src"]
        self.ip_dst = json_file["ip_dst"]
        self.src_port = json_file["src_port"]
        self.dst_port = json_file["dst_port"]
        self.banda = json_file["banda"]
        self.prioridade = json_file["prioridade"]
        self.classe = json_file["classe"]

        return True

    def toString(self):
        print("Contrato: ip_src:%s; ip_dst:%s; src_port:%s; dst_port:%s; proto:%s; dscp:%s; classe:%s; prioridade:%s; banda:%s;")
    
    def toJSON(self):
        return ''
    


    


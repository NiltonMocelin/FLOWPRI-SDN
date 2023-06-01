# Example for creating your program by specifying buffers to send, without relaying on pcap file

from trex.astf.api import *
import argparse


# we can send either Python bytes type as below:
http_req = b'GET /3384 HTTP/1.1\r\nHost: 22.0.0.3\r\nConnection: Keep-Alive\r\nUser-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)\r\nAccept: */*\r\nAccept-Language: en-us\r\nAccept-Encoding: gzip, deflate, compress\r\n\r\n'
# or we can send Python string containing ascii chars, as below:

def get_running_ascii (size):
    s='';
    c=65;
    for i in range(0,size):
        s+=chr(c)
        c+=1;
        if c==91:
            c=65
    return(s);

http_response = 'HTTP/1.1 200 OK\r\nServer: Microsoft-IIS/6.0\r\nContent-Type: text/html\r\nContent-Length: 32000\r\n\r\n<html><pre>'+get_running_ascii(11*1024)+'</pre></html>'

class Prof1():
    def __init__(self):
        pass  # tunables

    def create_profile(self):
        # client commands
        prog_c = ASTFProgram()
        prog_c.connect();
        prog_c.send(http_req)
        prog_c.recv(len(http_response))
        prog_c.delay(10);

        prog_s = ASTFProgram()
        prog_s.recv(len(http_req))
        prog_s.delay(10);
        prog_s.send_chunk(http_response,1100,10)
        prog_s.wait_for_peer_close()


        # ip generator
        ip_gen_c = ASTFIPGenDist(ip_range=["16.0.0.0", "16.0.0.255"], distribution="seq")
        ip_gen_s = ASTFIPGenDist(ip_range=["48.0.0.0", "48.0.255.255"], distribution="seq")
        ip_gen = ASTFIPGen(glob=ASTFIPGenGlobal(ip_offset="1.0.0.0"),
                           dist_client=ip_gen_c,
                           dist_server=ip_gen_s)

        info = ASTFGlobalInfo()
        info.tcp.mss = 1100
        #info.tcp.rxbufsize = 1102  # split the buffer to MSS and ack every buffer, no need the no_delay option
        #info.tcp.txbufsize = 1100
        info.tcp.initwnd = 1
        #info.tcp.no_delay = 0
        info.tcp.do_rfc1323 =0

        # template
        temp_c = ASTFTCPClientTemplate(program=prog_c,  ip_gen=ip_gen)
        temp_s = ASTFTCPServerTemplate(program=prog_s)  # using default association
        template = ASTFTemplate(client_template=temp_c, server_template=temp_s)

        # profile
        profile = ASTFProfile(default_ip_gen=ip_gen, templates=template,
                              default_c_glob_info=info,
                              default_s_glob_info=info)
        return profile

    def get_profile(self, tunables, **kwargs):
        parser = argparse.ArgumentParser(description='Argparser for {}'.format(os.path.basename(__file__)), 
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        args = parser.parse_args(tunables)
        return self.create_profile()


def register():
    return Prof1()

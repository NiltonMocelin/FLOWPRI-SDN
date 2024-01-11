from time import sleep
import eventlet
from eventlet import wsgi
from eventlet import websocket
from threading import Thread
import six

# demo app
import os
import random


#################################
# comunicacao interface web x controlador

PORTA_WEBS_RCV = 9998 #porta para receber solicitacoes de informacoes JSON para a interface WEB
PORTA_WEBS_SND = 9997 #porta para enviar informacoes JSON para a interface WEB
PORTA_ACCESS_WEB = 7000

def _websocket_rcv(json_request):
    """ Socket para receber solicitacoes a interface websocket """
    
    json_reply = """{
        "reply":[
            ["algo1": "valor1"],
            ["algo2": "valor2"]
            ]
        }"""

    return json_reply

def _websocket_snd(list_dados, tipo_dados):
    """ Socket para enviar informacoes a interface websocket """

    json_reply = """{"reply":"aa"}"""

    return json_reply
###################################

@websocket.WebSocketWSGI
def handle(ws):
    """  This is the websocket handler function.  Note that we
    can dispatch based on path in here, too."""
    if ws.path == '/echo':
        while True:
            m = ws.wait()
            if m is None:
                break
            ws.send(m)

    elif ws.path == '/data':
        for i in six.moves.range(10000):
            ws.send("0 %s %s\n" % (i, random.random()))
            eventlet.sleep(0.1)

def dispatch(environ, start_response):
    """ This resolves to the web page or the websocket depending on
    the path."""
    if environ['PATH_INFO'] == '/data':
        return handle(environ, start_response)
    else:
        start_response('200 OK', [('content-type', 'text/html')])
        return [open(os.path.join(
                    #  os.path.dirname(__file__),
                     'zzz.html')).read()]

def lancar_wsgi():
    print("lancando wsgi ...")
    listener = eventlet.listen(('localhost', PORTA_ACCESS_WEB))
    print("\nVisit http://localhost:%s/ in your websocket-capable browser.\n" % (PORTA_ACCESS_WEB))
    wsgi.server(listener, dispatch)

    print('Feito ...')



# if __name__ == "__main__":
#     # run an example app from the command line

#     t3 = Thread(target=lancar_wsgi)
#     t3.start()


#     for i in range(1000):
#         print(f'.')
#     sleep(5)
#     for i in range(1000):
#         print(f'.')
    
#     # eh bloqueante pqp print('nao eh bloqueante...')
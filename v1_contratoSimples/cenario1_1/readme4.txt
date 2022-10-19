Parece que usando innamespace=False, meio que todo mundo se "enxerga", as interfaces locais (onde o controlador sobe atualmente) e do mininet. Assim, podemos fazer algo para todo mundo poder se comunicar. Parece que tem uma possibilidade de o mininet não conseguir utilizar o loopback interface e então não consegue mandar mais mensagens, é preciso entender isso.
ref: https://pox-dev.noxrepo.narkive.com/8KtfIMxN/can-pox-connect-or-communicate-with-host


Aqui tem um exemplo de criar um "controller host"
ref principal: mesma da de cima
ref do codigo: https://github.com/brownsys/pane-demo-vm/blob/master/demos/PaneDemo.py#L56

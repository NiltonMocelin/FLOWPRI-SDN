#[build] sudo docker build -t flowpri-controller:1.0 .
#[run] sudo docker run -t flowpri-controller:1.0
#[obter-ids] docker images
#[remover-image] sudo docker image rm -f <image-id>

FROM alpine:3.12
RUN apk update && apk upgrade

#dependencias ryu
RUN apk add --no-cache build-base bash python3 pkgconfig gcc openldap libcurl python3-dev gpgme-dev libc-dev 

RUN apk add --no-cache py3-pip

#eh importante para instalacoes python modernas
RUN pip install wheel

RUN pip install netaddr
RUN pip install routes
RUN pip install setuptools
RUN pip install webob
RUN pip install oslo.config
RUN pip install msgpack-python
RUN pip install eventlet==0.30.2
RUN pip install stevedore
RUN pip install six
RUN pip install pbr
RUN pip install networkx

#instalar ryu
RUN pip install ryu

#install netifaces para obter ip local usando python
RUN pip install netifaces

#porta para receber contratos de hosts
EXPOSE 4444
#porta para troca de contratos entre controladores
EXPOSE 8888
#porta alcancavel pelos switches
EXPOSE 8000
#porta para o controlador receber programacao?

ADD flowpri.py flowpri.py

ENTRYPOINT ["ryu-manager", "flowpri.py", "--ofp-tcp-listen-port", "8000"]

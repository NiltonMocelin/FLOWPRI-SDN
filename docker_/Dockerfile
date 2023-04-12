#[build] sudo docker build -t flowpri-controller:1.0 .
#[run] sudo docker run -t flowpri-controller:1.0
#[obter-ids] docker images
#[remover-image] sudo docker image rm -f <image-id>

FROM alpine:3.12
RUN apk update && apk upgrade

#dependencias ryu
RUN apk add --no-cache build-base bash python3 pkgconfig gcc openldap libcurl python3-dev gpgme-dev libc-dev 

RUN apk add --no-cache py3-pip

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

EXPOSE 4444
EXPOSE 8888
ADD flowpri.py flowpri.py
#ENTRYPOINT ["python", "teste.py"]
# CMD ["python", "ryu-manager", "flowpri.py", "--ofp-tcp-listen-port", "8000"]
# CMD ["ls"]
#ADD flowpri.py flowpri.py
#ADD ryu/ ryu/
#RUN cd ryu/; pip install .
ENTRYPOINT ["ryu-manager", "flowpri.py", "--ofp-tcp-listen-port", "8000"]
#RUN ryu-manager flowpri.py --ofp-tcp-listen-port 8000
#CMD ["ryu","-v"]

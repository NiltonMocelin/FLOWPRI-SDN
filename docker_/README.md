# [RYU-CONTROLLER-SDN] Projeto FLOWPRI em docker container

- Objetivo: portar um controlador SDN RYU (FLOWPRI) em um container docker e modularizar multiplos controladores em uma mesma topologia mininet

- Deve servir como base para qualquer outro controlador baseado em RYU

- Qual problema resolve?: controladores são externos as redes mininet e apesar de ser possível rodar sobre NÓS externos ao mininet (Roots), eles compartilham a mesma tabela ROUTE. Assim, quando for responder um fluxo de dados, todos os controladores utilizam a primeira interface de rede correspondente da tabela ROUTE.
Ex: C1 está conectado a S1 por meio do root1, C2 está conectado a S2 por meio do root2. Quando C1 for responder C2, ele vai utilizar loopback. Isso foi resolvido em uma solucao (v3-flowpri) utilizando traduções de endereços de controladores. Os switches alteravam os endereços IP de controladores de modo que cada controlador tivesse uma tabela de endereços ficticios para outros, de modo que cada controlador soubesse exatamente qual interface de rede virtual deveria usar para se comunicar.

Utilizando containers, se espera conseguir isolar controladores e bindar interfaces para seus processos.

- [link-para conectar multiplas topologias mininet] https://mailman.stanford.edu/pipermail/mininet-discuss/2018-September/008064.html

## Aplicação: 

- Ser utilizado em cenários de simulação mininet

- É necessário que a topologia mininet possua NÓS externos ao mininet (Roots) conectados a portas dos switches internos da topologia.

	   Container1:FLOWPRI
		   |
[UserSpace]      Root		
		   |
--------------------------------------------
[MininetSpace]	   |
		  S1-------S2-----S3....
		 /  \
		H1  H2

- Desta forma, é possivel ter multiplos containers de controladores FLOWPRI.

## Dependencias

- Docker

## Como executar

- [build] sudo docker build -t flowpri-controller:1.0 .

- [run] sudo docker run -t flowpri-controller:1.0

# Remover

- [obter-ids-das-imagens] docker images

- [remover-image] sudo docker image rm -f <image-id>

##BASE docker

####https://medium.com/oracledevs/create-a-simple-docker-container-with-a-python-web-server-26534205061a

 - Utiliza uma imagem alpine linux
 
 - Instala as dependencias necessárias para executar o ryu-manager

 - Exporta portas para fazer bind de endereços (escutar/realizar conexões)


#12/04
## Docker container build Objetivos {

	- Importar uma imagem que contenha os requisitos do ryu

	- Instalar pacotes necessários para o ryu

	- Instalar o ryu

	- Exportar as portas necessárias

}

## Questões de design container-ryu{

	- FROM python importa uma imagem ubuntu aparentemente, que pesa 900mb

	- Existem alternativas como utilizar python da imagem alpine linux, que reduz para 200mb

	- Utilizando alpine no momento

	- Para instalar pacotes dependencia de app python era necessario GCC, por isso, foi instalado o pacote build-base no alpine (segundo a wiki, era o jeito mais rapido)

	- Esse conjunto de pacotes aparentemente resolve os problemas de instalação pip package	relacionados a GCC e python.h missing{

	`RUN apk add --no-cache bash \
                        python \
                        pkgconfig \
                        gcc \
                        openldap \
                        libcurl \
                        python3-dev \
                        gpgme-dev \
                        libc-dev \`	
	
	- quando se usa --no-cache, nao precisa no fim fazer rm -rf /var/cache/apk/*

	- esse rm .... é para remover o cache de pacotes e deixar as imagens mais leves

	}
	
	
	### Os requisitos listados para instalar o ryu-controller são os seguintes pacotes e suas dependencias: 
	#### segundo https://janieltec.wordpress.com/2016/06/16/instalando-o-ryu-no-debian-8/ {

		- setuptools.

		`apt-get install python-setuptools`

		- routes

		`apt-get install python-routes`

		- netaddr

		`apt-get install python-netaddr`

		- python-dev

		`apt-get install python-dev`
		
		- python-pip

		`apt-get install python-pip`
		
		- webob
		
		`pip install webob`
		
		- oslo.config
		
		`pip install oslo.config`
		
		- msgpack-python

		`pip install msgpack-python`
		
		- eventlet

		`pip install eventlet`
		
		- stevedore

		`pip install stevedore`

		- six
		
		`pip install six`
				
		- netaddr

		`pip install netaddr`

		- networkx

		`pip install networkx`
	}
	
	
# Ainda em desenvolvimento
	- [atualmente] Como fazer o ryu-manager funcionar{
		- Nao foi testado
		- Nao foi verificado se os switches conseguem se comunicar
		- Nao foi testado dentro do cenario de testes do mininet
	}


    - para testar{

        - [build] 

	`sudo docker build -t flowpri-controller:1.0 .`
        
	- [run]

	` sudo docker run -t flowpri-controller:1.0`
        
	- [obter-ids]
	
	`docker images`

        - [remover-image]

	` sudo docker image rm -f <image-id>`

    }
}

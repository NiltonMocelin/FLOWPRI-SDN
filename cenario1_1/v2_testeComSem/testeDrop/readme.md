# Teste de funcionalidade Framework

* Objetivo: Demonstrar que em um cenário onde um fluxo de baixa prioridade consome muita banda, um fluxo de maior prioridade tem seus requisitos garantidos quando usando o Framework. Comparar com o cenário sem o Framework.

* Fluxo de stream de vídeo (fluxo de alta prioridade)
- h1 -> h4

* Fluxo de baixa prioridade iperf:
- 
- h2->h4

### Configuração do teste

* Qualidade do vídeo - video2.mp4:

- Resolução: 1920x1080
- Requisito de banda: +- 5Mbps


#### Cenário (topologia) - Framework:5c_1sc Vs semFramework:5switch

* Iniciar a topologia:
`sudo python topo5_v2.py`

* Executar o script de configuração de filas:
`sh switchQueueConf2.sh`

* Iniciar os hosts e controladores:
`xterm h1 h2 root1 root2 root3 root4 root5`

* Iniciar os controladores em cada root correspondente (root1..root5):
`ryu-manager c1_v2_semPrints.py --ofp-tcp-listen-port 7000`

`ryu-manager c2_v2_semPrints.py --ofp-tcp-listen-port 66`

`ryu-manager c3_v2_semPrints.py --ofp-tcp-listen-port 66`

`ryu-manager c4_v2_semPrints.py --ofp-tcp-listen-port 66`

`ryu-manager c5_v2_semPrints.py --ofp-tcp-listen-port 6666`

* Iperf entre h2-h4 para simular tráfego background:
``

* Criar o contrato entre h1-h4 para envio do fluxo de vídeo:
``

* Script stream ( video2.mp4 é mudo, não precisa do -ab 128000) em h1:
`ffmpeg -re -i video.mp4 -c:v copy -c:a aac -listen 1 -ar 44100 -ab 128000 -f flv rtmp://172.16.10.1:10000/live`

- RTMP usa tcp para conexão, por isso, também é preciso reservar largura de banda para volta...

- RTP usar udp para conexão, nesse caso, não é necessário configurar tráfego de volta...

* Abrir a conexão no vlc ou com ffplay - no vlc procurar estatísticas:
`ffplay -stats rtmp://127.0.0.1:10000/live`


### Configuração VLC

* VLC não inicia em modo root. Ele pega o id do usuário para verificar se é root ou não.
* O script abaixo altera o VLC de modo que ele não obtenha o uid, mas o pid. É um truque que funciona e não afeta a execução. Fonte: https://www.tecmint.com/run-vlc-media-player-as-root-in-linux/

`sudo sed -i 's/geteuid/getppid/' /usr/bin/vlc`

* [NAO TESTADO] Uma alternativa seria usar em modo wrapper
- Caso queira abrir em root, use vlc-wrapper.
- cvlc eh uma reducao de vlc -ldummy, entao se ajustar, consegue utilizar com root.

* Caso queira utilizar audio, alsa foi instalado:
`pulseaudio --start` 

* Caso não queira utilizar audio:
`pulseaudio --kill` 

* Ex de como abrir streaming, enviando pacotes de video para o ip destino:
cvlc -vvv video.mp4 --sout '#rtp{proto=udp, mux=ts,dst=10.0.0.2,port=8080,sdp=sap,name="video1"}'


## ERRO AO TENTAR EXECUTAR UM VIDEO COM FFPLAY

* Erro de "libGL no matching fbconfigs" e "failed to load driver swrast" fonte: https://unix.stackexchange.com/questions/589236/libgl-error-no-matching-fbconfigs-or-visuals-found-glxgears-error-docker-cu


* solucao para "libGL error: No matching fbConfigs or visuals found":

`export LIBGL_ALWAYS_INDIRECT=1`

* solucao para "libGL error: failed to load driver: swrast":

`sudo apt-get install -y mesa-utils libgl1-mesa-glx`

* solucao para "X Error of failed request:  BadRequest" ou similar:
`sudo apt-get install -y libgl1-mesa-glx:i386`

* solucao para "X Error of failed request:  BadValue" - reiniciar a maquina:
`sudo apt install nvidia-340`
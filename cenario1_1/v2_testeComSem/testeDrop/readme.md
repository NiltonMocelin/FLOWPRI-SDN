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
- Usando rtmp - tráfego de volta +- 32kbps

* Medir banda de um fluxo com iftop, ou com netstat(acho que não funciona com netstat):
`iftop -i <interface>`

`sudo netstat -tpn | grep 12345`

 - OBS: iftop mostra 3 valores de largura de banda, em ordem: media dos ultimos 2s, 10s e 40s --- fonte: https://manpages.ubuntu.com/manpages/kinetic/en/man8/iftop.8.html

 - OBS2: mplayer é melhor que ffplay


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


#### UM TESTE COM RTP (UDP) E UM COM RTMP(TCP):
* video_stream/video2.mp4

* h4 abrir servidor iperf:
`iper -s`

* h2 iperf h4
`iperf -b 10M -c 172.16.10.4`

* h3 iperf h4
`iperf -b 10M -c 172.16.10.4`

* Observar que a largura de banda do streaming cai para 1Mb . NOTE QUE: o video degrada um pouco no cliente, enquanto que o servidor de streaming não perde desempenho no tratamento do video, apenas a rede é afetada - o que valida o teste.
`iftop -i h4-eth0`

##### COM RTMP
* Obs: RTMP usa tcp, ou seja, necessita de tráfego de "volta" +- 32kb, ida +- 5Mb (testado com video2.mp4).
Logo, é preciso um contrato para este tráfego tbm - no caso do framework.

* h1 video streaming to h4:
`ffmpeg -re -i ../video_stream/video2.mp4 -c:v copy -c:a copy -listen 1 -ar 44100 -preset ultrafast -f flv rtmp://172.16.10.1:10000/live`

* h4 executar mplayer:
`mplayer rtmp://172.16.10.1:10000/live`

##### COM RTP - CANCELADO POR BAIXA QUALIDADE (não achei um modo de streamar com qualidade, rtmp tem qualidade muito superior e usa menos banda - só que é tráfego bilateral tcp)
* h1 video streaming to h4 - usando rtp:
` ffmpeg -re -i ../video_stream/video2.mp4 -c:v copy -c:a copy -listen 1 -ar 44100 -preset ultrafast -f rtp rtp://172.16.10.4:10000 -sdp_file foo.sdp`

* h1 video streamin para h4 - usando udp puro:
`ffmpeg -re -i ../video_stream/video2.mp4 -c:v copy -c:a copy -listen 1 -ar 44100 -preset ultrafast -f mpegts udp://172.16.10.4:10000`

* h4 executar mplayer - rtp:
`mplayer foo.sdp` 

* h4 executar mplayer - udp:
`mplayer udp://172.16.10.4:10000` 



#####  TESTES ANTERIORES E PROCESSO DE APRENDIZAGEM

* Iperf entre h2-h4 para simular tráfego background:
``

* Criar o contrato entre h1-h4 para envio do fluxo de vídeo:
``

* Script stream ( video2.mp4 é mudo, não precisa do -ab 128000) em h1:

`ffmpeg -re -i video.mp4 -c:v copy -c:a aac -listen 1 -ar 44100 -ab 128000 -f flv rtmp://172.16.10.1:10000/live`

- RTMP usa tcp para conexão, por isso, também é preciso reservar largura de banda para volta...

- RTP usar udp para conexão, nesse caso, não é necessário configurar tráfego de volta...

* Abrir a conexão no vlc, ffplay ou mplayer - no vlc procurar estatísticas:

`ffplay -stats rtmp://127.0.0.1:10000/live`

`mplayer rtmp://127.0.0.1:10000/live`

* Para streaming por protocolos UDP é necessário um arquivo .sdp, que geralmente em aplicacoes de video é transferido por outro canal. Para gerar o .sdp, depois do comando do emissor adicionar o comando abaixo e usar isso para rodar com ffplay -i <file.sdp>:

` -sdp_file foo.sdp`

`ffplay -protocol_whitelist file,http,https,tcp,tls,rtp,udp -i foo.sdp`

`mplayer foo.sdp`

* Para limitar a largura de banda do ffmpeg em 2M, adicionar:
`-maxrate 2M`


### COM UDP:

* Emissor

`ffmpeg -re -i video2.mp4 -c:v copy -c:a aac -listen 1 -ar 44100 -f mpegts udp://192.168.1.71:10000`

* Receptor

`ffplay udp://192.168.1.71:10000`



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

* solucao para "X Error of failed request:  BadValue"  - depois reboot (fiz tanta coisa, pode ser que esses passos nao sejam o suficiente, mas depois deles funcionou):
`Ativar a aceleração 3D na maquina virtual`

`sudo apt-get install dkms build-essential`

`sudo dpkg -P $(dpkg -l | grep nvidia-driver | awk '{print $2}')`

`sudo apt autoremove`

`sudo apt install xserver-xorg-video-nouveau`


######### testes: 
[rtp:udp]

cvlc -vvv video2.mp4 :norm=ntsc :v4l2-width=320 :v4l2-height=240 :v4l2-
standard=45056 :channel=1 --no-sout-audio --sout '#transcode{vb="1600",vcodec=m
pgv,acodec=mpga,venc=ffmpeg}:rtp{proto=udp,mux=ts,dst=172.16.10.4,port=9000}' -
-loop --ttl 1

ffmpeg -re -i video2.mp4 -c:v copy -c:a aac -listen 1 -ar 44100 -f rtp 
rtp://172.16.10.4:10000


[rtmp:tcp]

* Se especificar o codec é possível mexer no bitrate, se não (usando copy), não consegue:
ffmpeg -re -i ../video_stream/video2.mp4 -preset ultrafast -vcodec libx 264 -b:v 5M -c:a aac -listen 1 -ar 44100 -maxrate 8M -minrate 8M -f flv rtmp://172.16.10.1:10000/live


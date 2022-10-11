Abra os hosts com xterm.

Se nao abrir video eh pq a variavel de ambiente $DISPLAY nao esta definida:
$ export DISPLAY=localhost:10.0

cvlc abre o vlc em modo command.
vlc nao abre com super usuario, entao:
$ su mininet, ou su - mininet, nao sei a diferenca.

Caso queira abrir em root, use vlc-wrapper.
cvlc eh uma reducao de vlc -ldummy, entao se ajustar, consegue utilizar com root.

Caso queira utilizar audio, alsa foi instalado:
$ pulseaudio --start #inicia
$ pulseaudio --kill #encerra

Para abrir streaming, enviando pacotes de video para o ip destino:
cvlc -vvv video.mp4 --sout '#rtp{proto=udp, mux=ts,dst=10.0.0.2,port=8080,sdp=sap,name="video1"}'

(-vvv eh para verbose nivel 2, alguns lugares dizem que eh para multiplas transmissoes mas parece nao ser verdade)

Para verificar a passagem dos pacotes no switch:
$ sudo tcpdump -i eth0 -s 0 udp #modificar conforme o protocolo de transporte e interface de comunicacao

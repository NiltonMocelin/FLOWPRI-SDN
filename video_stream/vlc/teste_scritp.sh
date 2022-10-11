export DISPLAY=localhost:10.0

echo "DISPLAY setado"

pulseaudio --start

echo "PulseAudio iniciado"

cvlc -vvv video.mp4 --sout '#rtp{proto=udp, mux=ts,dst=10.0.0.2,port=8080,sdp=sap,name="video1"}'

echo "Iniciando streaming: dst= rtp://10.0.0.2:8080 -- Video1"

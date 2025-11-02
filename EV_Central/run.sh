#!/bin/bash

# Uso: ./run.sh <IP> <PUERTO> <KAFKA_IP> <KAFKA_PORT>
# Ejemplo: ./run.sh 172.21.42.18 12345 172.21.42.17 9092

IP=${1:-0.0.0.0}          # Valor por defecto si no se pasa argumento
PORT=${2:-12345}
KAFKA_IP=${3:-172.21.42.17}
KAFKA_PORT=${4:-9092}

echo "Ejecutando con:"
echo "  IP: $IP"
echo "  Puerto: $PORT"
echo "  Kafka IP: $KAFKA_IP"
echo "  Kafka Puerto: $KAFKA_PORT"
echo

docker build -t central .
docker run -u=$(id -u $USER):$(id -g $USER) \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v $(pwd)/app:/app \
  -v $(pwd)/data:/data \
  -p 0.0.0.0:"$PORT":"$PORT" \
  --rm -it central \
  --ip "$IP" \
  --port "$PORT" \
  --kafka-ip "$KAFKA_IP" \
  --kafka-port "$KAFKA_PORT"

#docker run -u=$(id -u $USER):$(id -g $USER) -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw -v $(pwd)/app:/app --rm -it central --ip 172.21.42.18 --port 12345 --kafka-ip 172.21.42.17 --kafka-port 9092
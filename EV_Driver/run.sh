#!/bin/bash
ID=${1:-1}
KAFKA_IP=${2:-172.21.42.17}
KAFKA_PORT=${3:-9092}
docker build -t driver .
docker run -it driver --id $ID --kafka-ip $KAFKA_IP --kafka-port $KAFKA_PORT
#!/bin/bash
ID=${1:-1}
CENTRAL_IP=${2:-172.21.42.17}
CENTRAL_PORT=${3:-9092}
ENGINE_IP=${4:-172.21.42.17}
ENGINE_PORT=${5:-9092}
docker build -t monitor .
docker run -it monitor --id $ID --central-ip $CENTRAL_IP --central-port $CENTRAL_PORT --engine-ip $ENGINE_IP --engine-port $ENGINE_PORT
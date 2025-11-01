#!/bin/bash

ID=${1:-1}
KAFKA_IP=${2:-172.21.42.17}
KAFKA_PORT=${3:-9092}

# Crear volumen si no existe
docker volume inspect recover_files >/dev/null 2>&1 || docker volume create recover_files

# Construir imagen
docker build -t driver .

# Ejecutar contenedor
docker run --rm -v recover_files:/var/recover -it driver --id "$ID" --kafka-ip "$KAFKA_IP" --kafka-port "$KAFKA_PORT"

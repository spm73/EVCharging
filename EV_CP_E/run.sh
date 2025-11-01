#!/bin/bash

# Parámetros posicionales con valores por defecto
KAFKA_IP=${1:-172.21.42.17}
KAFKA_PORT=${2:-9092}
SERVER_IP=${3:-172.21.42.17}
SERVER_PORT=${4:-9092}

# Parámetro opcional: --location <valor>
LOCATION=""

# Recorre argumentos para encontrar --location
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --location)
            LOCATION="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Mostrar configuración antes de ejecutar
echo "Usando configuración:"
echo "  Kafka IP: $KAFKA_IP"
echo "  Kafka Port: $KAFKA_PORT"
echo "  Server IP: $SERVER_IP"
echo "  Server Port: $SERVER_PORT"
echo "  Location: ${LOCATION:-no especificado}"
echo

# Construir la imagen
docker build -t engine .

# Ejecutar contenedor con parámetros
docker run -it engine \
  --kafka-ip "$KAFKA_IP" \
  --kafka-port "$KAFKA_PORT" \
  --server-ip "$SERVER_IP" \
  --server-port "$SERVER_PORT" \
  ${LOCATION:+--location "$LOCATION"}

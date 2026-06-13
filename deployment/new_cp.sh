#!/bin/bash

# ==========================================================
# Script to provision and launch a new Charging Point (CP)
# Creates certificates (via gen_cp_cert.sh), generates a
# docker-compose, and starts the Engine + Monitor containers.
# ==========================================================

set -e

# ── Resolve project root ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CERTS_DIR="$PROJECT_ROOT/certificates"

# ── Colors ──
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   ⚡ New Charging Point Provisioning Script     ${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# ── 1. Collect CP parameters ──
read -p "$(echo -e "${YELLOW}👉 CP ID (e.g., CP-003): ${NC}")" CP_ID
if [ -z "$CP_ID" ]; then
    echo -e "${RED}❌ CP ID cannot be empty.${NC}"
    exit 1
fi

CP_NUM=$(echo "$CP_ID" | grep -oE '[0-9]+' | sed 's/^0*//')
if [ -z "$CP_NUM" ]; then
    echo -e "${RED}❌ Could not extract a number from CP ID '$CP_ID'.${NC}"
    exit 1
fi

read -p "$(echo -e "${YELLOW}📍 Location (e.g., Valencia): ${NC}")" CP_LOCATION
CP_LOCATION="${CP_LOCATION:-Unknown}"

read -p "$(echo -e "${YELLOW}💶 Price per kWh (e.g., 0.25): ${NC}")" CP_PRICE
CP_PRICE="${CP_PRICE:-0.25}"

# ── 2. Collect network IPs (separate machines in real deployment) ──
echo ""
echo -e "${CYAN}── Network Configuration ──${NC}"
echo -e "  In a real deployment, these services run on different machines."
echo ""

read -p "$(echo -e "${YELLOW}🖥️  Central IP  (e.g., 192.168.18.10): ${NC}")" CENTRAL_IP
CENTRAL_IP="${CENTRAL_IP:-192.168.18.13}"
read -p "$(echo -e "${YELLOW}    Central socket port [7000]: ${NC}")" CENTRAL_PORT
CENTRAL_PORT="${CENTRAL_PORT:-7000}"

read -p "$(echo -e "${YELLOW}📋 Registry IP (e.g., 192.168.18.10): ${NC}")" REGISTRY_IP
REGISTRY_IP="${REGISTRY_IP:-$CENTRAL_IP}"
read -p "$(echo -e "${YELLOW}    Registry port [8000]: ${NC}")" REGISTRY_PORT
REGISTRY_PORT="${REGISTRY_PORT:-8000}"

read -p "$(echo -e "${YELLOW}📨 Kafka Broker IP (e.g., 192.168.18.10): ${NC}")" KAFKA_IP
KAFKA_IP="${KAFKA_IP:-$CENTRAL_IP}"
read -p "$(echo -e "${YELLOW}    Kafka Broker port [9092]: ${NC}")" KAFKA_PORT
KAFKA_PORT="${KAFKA_PORT:-9092}"

read -p "$(echo -e "${YELLOW}🔌 Engine IP (IP of THIS machine) (e.g., 192.168.18.15): ${NC}")" ENGINE_IP
ENGINE_IP="${ENGINE_IP:-$CENTRAL_IP}"

ENGINE_HOST_PORT=$((9000 + CP_NUM - 1))
read -p "$(echo -e "${YELLOW}    Engine host port [${ENGINE_HOST_PORT}]: ${NC}")" CUSTOM_PORT
ENGINE_HOST_PORT="${CUSTOM_PORT:-$ENGINE_HOST_PORT}"

# ── 3. Summary ──
echo ""
echo -e "${CYAN}── Summary ──${NC}"
echo -e "  CP ID:          ${GREEN}${CP_ID}${NC}"
echo -e "  Location:       ${GREEN}${CP_LOCATION}${NC}"
echo -e "  Price/kWh:      ${GREEN}${CP_PRICE} €${NC}"
echo -e "  Central:        ${GREEN}${CENTRAL_IP}:${CENTRAL_PORT}${NC}"
echo -e "  Registry:       ${GREEN}${REGISTRY_IP}:${REGISTRY_PORT}${NC}"
echo -e "  Kafka:          ${GREEN}${KAFKA_IP}:${KAFKA_PORT}${NC}"
echo -e "  Engine:         ${GREEN}${ENGINE_IP}:${ENGINE_HOST_PORT}${NC}"
echo ""
read -p "$(echo -e "${YELLOW}Proceed? [Y/n]: ${NC}")" CONFIRM
if [[ "$CONFIRM" =~ ^[Nn] ]]; then
    echo "Aborted."
    exit 0
fi

# ── 4. Generate SSL certificate using gen_cp_cert.sh ──
CERT_OUT_DIR="$CERTS_DIR/certs_cp${CP_NUM}"

if [ -d "$CERT_OUT_DIR" ] && [ -f "$CERT_OUT_DIR/cp.crt" ]; then
    echo -e "${YELLOW}⚠️  Certificate directory $CERT_OUT_DIR already exists. Reusing existing certs.${NC}"
else
    echo -e "${CYAN}🔐 Generating SSL certificate for ${CP_ID}...${NC}"

    if [ ! -f "$CERTS_DIR/gen_cp_cert.sh" ]; then
        echo -e "${RED}❌ gen_cp_cert.sh not found in $CERTS_DIR${NC}"
        exit 1
    fi

    # Run gen_cp_cert.sh from the certificates directory, piping the CP_ID
    (cd "$CERTS_DIR" && echo "$CP_ID" | bash gen_cp_cert.sh)

    # gen_cp_cert.sh creates cp_<CP_ID>.key and cp_<CP_ID>.crt in the certs dir.
    # Move them to the expected directory with the standard names.
    PREFIX="cp_${CP_ID}"
    mkdir -p "$CERT_OUT_DIR"
    mv "$CERTS_DIR/${PREFIX}.key" "$CERT_OUT_DIR/cp.key"
    mv "$CERTS_DIR/${PREFIX}.crt" "$CERT_OUT_DIR/cp.crt"

    echo -e "${GREEN}✅ Certificate generated and placed in:${NC}"
    echo "     🔑 $CERT_OUT_DIR/cp.key"
    echo "     📜 $CERT_OUT_DIR/cp.crt"
fi

# ── 5. Generate docker-compose file ──
COMPOSE_DIR="$PROJECT_ROOT/deployment/cp${CP_NUM}"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yml"

mkdir -p "$COMPOSE_DIR"

echo -e "${CYAN}📄 Generating docker-compose at ${COMPOSE_FILE}...${NC}"

cat > "$COMPOSE_FILE" <<EOF
# Auto-generated docker-compose for ${CP_ID}
services:
  ev_engine_${CP_NUM}:
    build:
      context: ../..
      dockerfile: EV_CP_E/Dockerfile
    container_name: ev_engine_${CP_NUM}
    ports:
      - "${ENGINE_HOST_PORT}:9000"
    environment:
      - ENGINE_HOST=0.0.0.0
      - ENGINE_PORT=9000
      - KAFKA_BROKER_HOST=${KAFKA_IP}
      - KAFKA_BROKER_PORT=${KAFKA_PORT}
    volumes:
      - cp${CP_NUM}_engine_data:/data

  ev_monitor_${CP_NUM}:
    build:
      context: ../..
      dockerfile: EV_CP_M/Dockerfile
    container_name: ev_monitor_${CP_NUM}
    environment:
      - TERM=xterm-256color
      - CP_ID=${CP_ID}
      - CP_LOCATION=${CP_LOCATION}
      - PRICE_PER_KWH=${CP_PRICE}
      - CENTRAL_HOST=${CENTRAL_IP}
      - CENTRAL_PORT=${CENTRAL_PORT}
      - ENGINE_HOST=${ENGINE_IP}
      - ENGINE_PORT=${ENGINE_HOST_PORT}
      - REGISTRY_HOST=${REGISTRY_IP}
      - REGISTRY_PORT=${REGISTRY_PORT}
    volumes:
      - ../../certificates/certs_cp${CP_NUM}/cp.crt:/certs/cp.crt:ro
      - ../../certificates/certs_cp${CP_NUM}/cp.key:/certs/cp.key:ro
      - cp${CP_NUM}_monitor_data:/data
    stdin_open: true
    tty: true

volumes:
  cp${CP_NUM}_engine_data:
  cp${CP_NUM}_monitor_data:
EOF

echo -e "${GREEN}✅ docker-compose generated.${NC}"

# ── 6. Build and launch ──
echo ""
read -p "$(echo -e "${YELLOW}🚀 Build and start containers now? [Y/n]: ${NC}")" LAUNCH
if [[ "$LAUNCH" =~ ^[Nn] ]]; then
    echo -e "${CYAN}Done! To start later, run:${NC}"
    echo "  docker compose -f $COMPOSE_FILE up --build -d"
    exit 0
fi

echo -e "${CYAN}🔨 Building and starting ${CP_ID}...${NC}"
docker compose -f "$COMPOSE_FILE" up --build -d

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   🎉 ${CP_ID} is now running!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "  Engine:  container ${CYAN}ev_engine_${CP_NUM}${NC} on port ${ENGINE_HOST_PORT}"
echo -e "  Monitor: container ${CYAN}ev_monitor_${CP_NUM}${NC}"
echo ""
echo -e "  To attach to the monitor: ${YELLOW}docker attach ev_monitor_${CP_NUM}${NC}"
echo -e "  To stop:                  ${YELLOW}docker compose -f $COMPOSE_FILE down${NC}"
echo -e "  To view logs:             ${YELLOW}docker compose -f $COMPOSE_FILE logs -f${NC}"

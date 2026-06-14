#!/bin/bash

# ==========================================================
# Script to provision and launch a new EV_Driver instance
# Generates a dedicated directory and docker-compose file.
# Fully autonomous: asks for network configuration interactively.
# ==========================================================

set -e

# ── Resolve project root ──
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Colors ──
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   🚗 New EV_Driver Provisioning Script          ${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""

# ── 1. Collect Driver ID ──
read -p "$(echo -e "${YELLOW}👉 Driver ID (e.g., DRV-001): ${NC}")" DRIVER_ID
if [ -z "$DRIVER_ID" ]; then
    echo -e "${RED}❌ Driver ID cannot be empty.${NC}"
    exit 1
fi

# Extract the numeric part to name directories and volumes systematically
DRV_NUM=$(echo "$DRIVER_ID" | grep -oE '[0-9]+' | sed 's/^0*//')
if [ -z "$DRV_NUM" ]; then
    echo -e "${RED}❌ Could not extract a number from Driver ID '$DRIVER_ID'.${NC}"
    exit 1
fi

# ── 2. Collect Network Configurations ──
echo ""
echo -e "${CYAN}── Network Configuration ──${NC}"
echo -e "  Leave blank and press Enter to use the default values."
echo ""

read -p "$(echo -e "${YELLOW}📨 Kafka Broker IP (e.g., 192.168.18.10): ${NC}")" KAFKA_IP
KAFKA_IP="${KAFKA_IP:-192.168.18.13}"

read -p "$(echo -e "${YELLOW}    Kafka Broker port [9092]: ${NC}")" KAFKA_PORT
KAFKA_PORT="${KAFKA_PORT:-9092}"


# ── 3. Summary ──
echo ""
echo -e "${CYAN}── Summary ──${NC}"
echo -e "  Driver ID:          ${GREEN}${DRIVER_ID}${NC}"
echo -e "  Kafka Broker:       ${GREEN}${KAFKA_IP}:${KAFKA_PORT}${NC}"
echo -e "  Deployment Folder:  ${GREEN}deployment/driver${DRV_NUM}${NC}"
echo -e "  Isolated Volume:    ${GREEN}driver${DRV_NUM}_data${NC}"
echo ""
read -p "$(echo -e "${YELLOW}Proceed with provisioning? [Y/n]: ${NC}")" CONFIRM
if [[ "$CONFIRM" =~ ^[Nn] ]]; then
    echo "Aborted."
    exit 0
fi

# ── 4. Generate isolated deployment directory ──
COMPOSE_DIR="$PROJECT_ROOT/deployment/driver${DRV_NUM}"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yml"

mkdir -p "$COMPOSE_DIR"

echo -e "${CYAN}📄 Generating docker-compose at ${COMPOSE_FILE}...${NC}"

# ── 5. Write the custom docker-compose.yml ──
cat > "$COMPOSE_FILE" <<EOF
# Auto-generated docker-compose for ${DRIVER_ID}
services:
  ev_driver_${DRV_NUM}:
    build:
      context: ../..
      dockerfile: EV_Driver/Dockerfile
    container_name: ev_driver_${DRV_NUM}
    environment:
      - ID=${DRIVER_ID}
      - BROKER_IP=${KAFKA_IP}
      - BROKER_PORT=${KAFKA_PORT}
      - SAVED_FILE=/system/saved.txt
      - CPS_FILE=/system/cps.txt
      - TERM=xterm-256color
    entrypoint: [ "/bin/sh", "-c" ]
    command: >
      "
      export IP=\$(hostname -i | awk '{print \$1}');
      exec uv run --package ev-driver python -m EV_Driver.main
      "
    volumes:
      - driver${DRV_NUM}_data:/system
    stdin_open: true
    tty: true

volumes:
  driver${DRV_NUM}_data:
EOF

echo -e "${GREEN}✅ docker-compose generated successfully.${NC}"

# ── 6. Build and launch option ──
echo ""
read -p "$(echo -e "${YELLOW}🚀 Build and start container interactively now? [Y/n]: ${NC}")" LAUNCH
if [[ "$LAUNCH" =~ ^[Nn] ]]; then
    echo -e "${CYAN}Done! To start it later, run:${NC}"
    echo "  docker compose -f $COMPOSE_FILE run --rm ev_driver_${DRV_NUM}"
    exit 0
fi

echo -e "${CYAN}🔨 Building and launching ${DRIVER_ID}...${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   🚗 Starting interactive session for ${DRIVER_ID}...${NC}"
echo -e "${GREEN}================================================${NC}"

# Utilizamos run en lugar de up -d. 
# El flag --rm destruirá el contenedor al salir, pero el volumen de datos persistirá.
docker compose -f "$COMPOSE_FILE" run --rm "ev_driver_${DRV_NUM}"
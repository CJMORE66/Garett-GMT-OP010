#!/bin/bash

# IIoT Platform Deployment Script for Raspberry Pi CM5
# This script deploys the complete IIoT stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  IIoT Platform Deployment Script      ${NC}"
echo -e "${GREEN}  Raspberry Pi CM5                     ${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Warning: Not running as root. Some operations may require sudo.${NC}"
fi

# Change to script directory
cd "$(dirname "$0")"

echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker is not installed. Please install Docker first.${NC}" >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}Docker Compose is not installed.${NC}" >&2; exit 1; }
echo -e "${GREEN}Prerequisites check passed.${NC}"

echo -e "${YELLOW}Step 2: Creating required directories...${NC}"
mkdir -p mosquitto/config
mkdir -p influxdb
mkdir -p grafana/provisioning/dashboards
mkdir -p grafana/provisioning/datasources
mkdir -p nodered
mkdir -p models
mkdir -p config
mkdir -p services/opc-ua-collector
mkdir -p services/ml-inference
mkdir -p services/product-tracker
mkdir -p services/data-writer
echo -e "${GREEN}Directories created.${NC}"

echo -e "${YELLOW}Step 3: Creating environment file...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}Created .env from template. Please edit it with your settings.${NC}"
else
    echo -e "${GREEN}.env already exists.${NC}"
fi

echo -e "${YELLOW}Step 4: Building and starting services...${NC}"
docker-compose build --no-cache
docker-compose up -d

echo -e "${YELLOW}Step 5: Waiting for services to be ready...${NC}"
sleep 10

# Check service status
echo -e "${YELLOW}Service Status:${NC}"
docker-compose ps

# Wait for specific services
echo -e "${YELLOW}Waiting for InfluxDB...${NC}"
for i in {1..30}; do
    if docker exec influxdb curl -s http://localhost:8086/health >/dev/null 2>&1; then
        echo -e "${GREEN}InfluxDB is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo -e "${YELLOW}Waiting for PostgreSQL...${NC}"
for i in {1..30}; do
    if docker exec postgres pg_isready -U iot_user -d product_history >/dev/null 2>&1; then
        echo -e "${GREEN}PostgreSQL is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo -e "${YELLOW}Waiting for Mosquitto...${NC}"
for i in {1..10}; do
    if docker exec mosquitto netstat -tuln | grep -q 1883; then
        echo -e "${GREEN}Mosquitto is ready!${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Deployment Complete!                 ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Access points:"
echo -e "  Grafana:      http://<raspberry-ip>:3000"
echo -e "  Node-RED:     http://<raspberry-ip>:1880"
echo -e "  InfluxDB UI:  http://<raspberry-ip>:8086"
echo ""
echo -e "Default credentials:"
echo -e "  Grafana:      admin / iotadmin2024"
echo -e "  InfluxDB:     admin / iotadmin2024"
echo -e "  PostgreSQL:   iot_user / iotpass2024"
echo ""
echo -e "MQTT Topics:"
echo -e "  Telemetry:    op10/telemetry/#"
echo -e "  ML Results:   op10/ml/results"
echo -e "  Alerts:       op10/alerts/#"
echo -e "  Products:     op10/product/#"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Edit .env with your PLC IP address"
echo -e "2. Configure PLC UDT structures (see docs/UDT_STRUCTURES.md)"
echo -e "3. Import Grafana dashboards from grafana/provisioning/dashboards/"
echo -e "4. Import Node-RED flows from nodered/flows.json"
echo -e "5. Train ML models with historical data (see services/ml-inference/)"
echo ""

# IIoT Platform for OP10 - Raspberry Pi Implementation

## Project Overview

This project implements a complete IIoT solution for the OP10 manufacturing station, including:
- **Telemetry Collection**: OPC UA client for real-time data from PLC
- **Predictive Maintenance**: ML-based anomaly detection and RUL prediction
- **Product History Tracking**: Full traceability of all products
- **Visualization**: Grafana dashboards for monitoring

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    PLC      │────▶│   OPC UA    │────▶│   MQTT      │
│  (TIA Portal)│     │  Collector  │     │   Broker    │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
        ┌──────────────────────────────────────┼──────────────────────────────────────┐
        │                                      │                                      │
        ▼                                      ▼                                      ▼
┌─────────────┐                       ┌─────────────┐                       ┌─────────────┐
│  InfluxDB   │                       │  ML Engine  │                       │  Redis      │
│  (telemetry)│◀──────────────────────│  (predict)  │──────────────────────▶│  (cache)    │
└─────────────┘                       └─────────────┘                       └─────────────┘
        │                                      │
        │                                      │
        ▼                                      ▼
┌─────────────┐                       ┌─────────────┐
│  Grafana    │                       │  Alerts     │
│  (dashboards)│                      │  (Slack/SMS)│
└─────────────┘                       └─────────────┘
```

## Quick Start

```bash
# Clone and start all services
git clone <repo>
cd iiot-project
docker-compose up -d

# Check status
docker-compose ps
```

## Project Structure

```
iiot-project/
├── docker-compose.yml
├── mosquitto/
│   └── config/
│       └── mosquitto.conf
├── services/
│   ├── opc-ua-collector/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── main.py
│   ├── ml-inference/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── inference.py
│   ├── product-tracker/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── main.py
│   └── data-writer/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── writer.py
├── models/
│   └── README.md
├── grafana/
│   └── provisioning/
│       ├── dashboards/
│       └── datasources/
└── docs/
    ├── UDT_STRUCTURES.md
    └── API_DOCUMENTATION.md
```

## Hardware Requirements

- Raspberry Pi CM5 16GB RAM
- SSD 64GB+ (USB 3.0)
- Network connectivity to PLC (192.168.1.100)

## Software Requirements

- Raspberry Pi OS Lite 64-bit
- Docker 25.x
- Docker Compose v2

## License

MIT

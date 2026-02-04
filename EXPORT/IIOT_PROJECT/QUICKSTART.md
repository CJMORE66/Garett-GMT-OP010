# Quick Start Guide

## Co bylo vytvořeno

| Komponenta | Status |
|------------|--------|
| Docker Compose Stack | ✅ Hotovo |
| OPC UA Collector | ✅ Hotovo |
| ML Inference Service | ✅ Hotovo |
| Product Tracker | ✅ Hotovo |
| Data Writer | ✅ Hotovo |
| Grafana Dashboards | ✅ Hotovo |
| Node-RED Flows | ✅ Hotovo |
| PostgreSQL Schema | ✅ Hotovo |
| UDT Dokumentace | ✅ Hotovo |
| Deployment Scripts | ✅ Hotovo |
| API Documentation | ✅ Hotovo |

## Manuální kroky na Raspberry Pi CM5

### Krok 1: Příprava OS

```bash
# Připojte SD kartu s Raspberry Pi OS Lite 64-bit
# Nebo použijte Raspberry Pi Imager

# Přihlaste se přes SSH
ssh pi@<ip-adresa>
# heslo: raspberry
```

### Krok 2: Konfigurace sítě

```bash
# Editujte /etc/dhcpcd.conf pro statickou IP
sudo nano /etc/dhcpcd.conf

# Přidejte:
interface eth0
static ip_address=192.168.1.200/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1
```

### Krok 3: Připojení SSD

```bash
# Připojte SSD disk
sudo fdisk -l  # Zjistěte zařízení
sudo mkfs.ext4 /dev/sda1  # Formátujte
sudo mount /dev/sda1 /data

# Přidejte do /etc/fstab pro automatické připojení
echo "/dev/sda1 /data ext4 defaults,nofail 0 0" | sudo tee -a /etc/fstab
```

### Krok 4: Instalace Docker

```bash
# Aktualizujte systém
sudo apt update && sudo apt upgrade -y

# Nainstalujte Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Přidejte uživatele do docker skupiny
sudo usermod -aG docker pi

# Nainstalujte Docker Compose
sudo apt install docker-compose -y
```

### Krok 5: Konfigurace času

```bash
# Nainstalujte chrony pro synchronizaci s PLC
sudo apt install chrony -y

# Editujte konfiguraci
sudo nano /etc/chrony/chrony.conf

# Přidejte NTP server vašeho PLC nebo lokální server
server 192.168.1.100 iburst

sudo systemctl restart chrony
```

### Krok 6: Přenos projektu

```bash
# Přeneste projekt na Raspberry Pi
scp -r IIOT_PROJECT/ pi@192.168.1.200:/home/pi/

# Nebo klonujte z Git
git clone <repo-url>
cd IIOT_PROJECT
```

### Krok 7: Spuštění

```bash
# Nastavte oprávnění deploy skriptu
chmod +x deploy.sh

# Spusťte deployment
./deploy.sh
```

## Struktura projektu

```
IIOT_PROJECT/
├── docker-compose.yml          # Hlavní konfigurace
├── deploy.sh                   # Deployment script (Linux)
├── deploy.ps1                  # Deployment script (Windows)
├── .env.example                # Šablona konfigurace
├── README.md                   # Hlavní dokumentace
├── QUICKSTART.md               # Tento soubor
│
├── mosquitto/
│   └── config/mosquitto.conf   # MQTT broker config
│
├── influxdb/
│   └── config.yml              # InfluxDB config
│
├── grafana/
│   └── provisioning/           # Dashboardy a datasources
│       ├── datasources/influxdb.yml
│       ├── dashboards/plant-overview.json
│       └── dashboards/providers.yml
│
├── nodered/
│   └── flows.json              # Node-RED flow
│
├── postgres/
│   └── init.sql                # PostgreSQL schéma
│
├── services/
│   ├── opc-ua-collector/       # Sběr dat z PLC
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── main.py
│   │
│   ├── ml-inference/           # ML predikce
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── inference.py
│   │
│   ├── product-tracker/        # Sledování produktů
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── main.py
│   │
│   └── data-writer/            # Zápis do databází
│       ├── Dockerfile
│       ├── requirements.txt
│       └── writer.py
│
├── models/                     # ML modely (ONNX)
│   ├── README.md
│   └── anomaly_detector.onnx   # Placeholder
│
├── config/                     # Konfigurační soubory
│   ├── config.yaml
│   ├── ml_config.yaml
│   └── tracker_config.yaml
│
└── docs/
    ├── UDT_STRUCTURES.md       # PLC UDT dokumentace
    └── API_DOCUMENTATION.md    # MQTT/API dokumentace
```

## Přístup k službám

| Služba | URL | Uživatel | Heslo |
|--------|-----|----------|-------|
| Grafana | http://192.168.1.200:3000 | admin | iotadmin2024 |
| InfluxDB | http://192.168.1.200:8086 | admin | iotadmin2024 |
| Node-RED | http://192.168.1.200:1880 | - | - |
| PostgreSQL | 192.168.1.200:5432 | iot_user | iotpass2024 |
| MQTT | 192.168.1.200:1883 | - | - |

## Další kroky

1. **Upravte .env soubor** s vaší PLC IP adresou
2. **Vytvořte UDT struktury** v TIA Portal podle `docs/UDT_STRUCTURES.md`
3. **Importujte dashboardy** do Grafany
4. **Importujte Node-RED flow** z `nodered/flows.json`
5. **Trénujte ML modely** s historickými daty
6. **Otestujte integraci** s PLC

## Troubleshooting

```bash
# Kontrola logů
docker-compose logs -f

# Kontrola stavu služeb
docker-compose ps

# Restart služby
docker-compose restart <service_name>

# Připojení do kontejneru
docker exec -it <container_name> /bin/bash
```

## Podpora

- MQTT Topics: `op10/telemetry/#`, `op10/ml/#`, `op10/alerts/#`
- Dokumentace: `docs/`
- Příklady: `services/*/main.py`

# IIoT Platform Deployment Script for Windows (Development/Testing)
# This script deploys the IIoT stack for testing purposes

Write-Host "========================================" -ForegroundColor Green
Write-Host "  IIoT Platform Deployment Script      " -ForegroundColor Green
Write-Host "  Windows (Development Mode)           " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Step 1: Checking prerequisites..." -ForegroundColor Yellow

# Check for Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "Docker found: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check for Docker Compose
try {
    $composeVersion = docker-compose --version 2>&1
    Write-Host "Docker Compose found: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

Write-Host "Step 2: Creating required directories..." -ForegroundColor Yellow
$dirs = @("mosquitto/config", "influxdb", "grafana/provisioning/dashboards", 
          "grafana/provisioning/datasources", "nodered", "models", "config",
          "services/opc-ua-collector", "services/ml-inference", 
          "services/product-tracker", "services/data-writer")

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Gray
    }
}

Write-Host "Step 3: Creating environment file..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from template. Please edit it with your settings." -ForegroundColor Yellow
} else {
    Write-Host ".env already exists." -ForegroundColor Green
}

Write-Host "Step 4: Building and starting services..." -ForegroundColor Yellow
docker-compose build --no-cache
docker-compose up -d

Write-Host "Step 5: Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check service status
Write-Host "Service Status:" -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!                 " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access points (localhost):"
Write-Host "  Grafana:      http://localhost:3000"
Write-Host "  Node-RED:     http://localhost:1880"
Write-Host "  InfluxDB:     http://localhost:8086"
Write-Host ""
Write-Host "Default credentials:"
Write-Host "  Grafana:      admin / iotadmin2024"
Write-Host "  InfluxDB:     admin / iotadmin2024"
Write-Host "  PostgreSQL:   iot_user / iotpass2024"
Write-Host ""
Write-Host "Note: For production, deploy on Raspberry Pi with actual PLC connection." -ForegroundColor Yellow

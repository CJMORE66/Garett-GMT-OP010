# API Documentation

## MQTT Topics

### Telemetry

**Topic:** `op10/telemetry/{node_id}`

**Payload:**
```json
{
    "timestamp": "2024-02-02T14:30:00Z",
    "node_id": "ns=2;s=DB50.RealVibrationX",
    "value": 0.0234,
    "quality": "good"
}
```

### Product Events

**Topic:** `op10/product/created`

**Payload:**
```json
{
    "serial_number": "SN-2024-001256",
    "batch_number": "B-2024-0142",
    "product_type_id": 1,
    "variant_id": 3,
    "customer_id": 1,
    "work_order_id": "WO-2024-0089"
}
```

**Topic:** `op10/product/step_entry`

**Payload:**
```json
{
    "serial_number": "SN-2024-001256",
    "step_number": 3,
    "step_name": "FLOW2",
    "station_id": "ST10_FLOW2",
    "position_id": "P3"
}
```

**Topic:** `op10/product/step_exit`

**Payload:**
```json
{
    "serial_number": "SN-2024-001256",
    "step_number": 3,
    "step_name": "FLOW2",
    "station_id": "ST10_FLOW2",
    "result": "pass",
    "cycle_count": 1250
}
```

**Topic:** `op10/product/measurement`

**Payload:**
```json
{
    "serial_number": "SN-2024-001256",
    "step_id": 15,
    "measurement_name": "BoreDiameter",
    "value": 25.02,
    "unit": "mm",
    "min_limit": 24.98,
    "max_limit": 25.02,
    "target_value": 25.00,
    "station_id": "ST10_QC2",
    "sensor_id": "LASER-001"
}
```

**Topic:** `op10/product/completed`

**Payload:**
```json
{
    "serial_number": "SN-2024-001256",
    "quality_result": "ok"
}
```

### ML Results

**Topic:** `op10/ml/results`

**Payload:**
```json
{
    "timestamp": "2024-02-02T14:30:05Z",
    "anomaly": 0,
    "probability": 0.23,
    "rul_days": 85.5,
    "features_summary": {
        "rms_x": 0.0156,
        "rms_y": 0.0123,
        "rms_z": 0.0189,
        "temp_avg": 52.3
    }
}
```

### Alerts

**Topic:** `op10/alerts/anomaly`

**Payload:**
```json
{
    "timestamp": "2024-02-02T14:30:05Z",
    "probability": 0.85,
    "rul_days": 12.3
}
```

**Topic:** `op10/alerts/rul/warning`

**Payload:**
```json
{
    "timestamp": "2024-02-02T14:30:05Z",
    "machine_id": "ST10_CNC_01",
    "rul_days": 25.0,
    "threshold": 30.0
}
```

**Topic:** `op10/alerts/rul/critical`

**Payload:**
```json
{
    "timestamp": "2024-02-02T14:30:05Z",
    "machine_id": "ST10_CNC_01",
    "rul_days": 5.0,
    "threshold": 7.0
}
```

## InfluxDB Queries

### Vibration Data (Last 24 hours)
```flux
from(bucket: "telemetry")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "telemetry")
  |> filter(fn: (r) => r._field == "value")
  |> filter(fn: (r) => r.node_id == "ns=2;s=DB50.RealVibrationX")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
```

### Temperature Trend (Last 7 days)
```flux
from(bucket: "telemetry")
  |> range(start: -7d)
  |> filter(fn: (r) => r._measurement == "telemetry")
  |> filter(fn: (r) => r._field == "value")
  |> filter(fn: (r) => r.node_id == "ns=2;s=DB50.RealTempMotor")
  |> yield(name: "temperature")
```

### ML Results (Anomaly Detection)
```flux
from(bucket: "telemetry")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "ml_results")
  |> filter(fn: (r) => r._field == "probability" or r._field == "rul_days")
```

## PostgreSQL Queries

### Get Product History
```sql
SELECT p.*, ps.*, m.*
FROM products p
LEFT JOIN process_steps ps ON p.id = ps.product_id
LEFT JOIN measurements m ON p.id = m.product_id
WHERE p.serial_number = 'SN-2024-001256'
ORDER BY ps.step_number, m.measured_at;
```

### Get Batch Summary
```sql
SELECT
    batch_number,
    COUNT(*) as total,
    SUM(CASE WHEN quality_result = 'ok' THEN 1 ELSE 0 END) as passed,
    SUM(CASE WHEN quality_result = 'ng' THEN 1 ELSE 0 END) as failed,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_time_seconds
FROM products
WHERE batch_number = 'B-2024-0142'
GROUP BY batch_number;
```

### Get Station Performance (Last 24h)
```sql
SELECT
    ps.station_id,
    COUNT(*) as product_count,
    AVG(ps.processing_duration_ms) as avg_duration_ms,
    SUM(CASE WHEN ps.step_result = 'fail' THEN 1 ELSE 0 END) as failures
FROM process_steps ps
JOIN products p ON p.id = ps.product_id
WHERE ps.entry_time > NOW() - INTERVAL '24 hours'
GROUP BY ps.station_id
ORDER BY ps.station_id;
```

### Get Measurements with SPC
```sql
SELECT
    measurement_name,
    COUNT(*) as sample_count,
    AVG(value) as mean,
    STDDEV(value) as std_dev,
    MIN(value) as min_val,
    MAX(value) as max_val,
    AVG(deviation) as avg_deviation,
    AVG(cpk) as avg_cpk
FROM measurements
WHERE measured_at > NOW() - INTERVAL '24 hours'
GROUP BY measurement_name
ORDER BY measurement_name;
```

## Node-RED HTTP Endpoints (Optional)

### Product Search API
```
GET /api/products?serial=SN-2024-001256
GET /api/products?batch=B-2024-0142
GET /api/products?status=completed
```

### Product Detail
```
GET /api/products/:serial/history
GET /api/products/:serial/measurements
GET /api/products/:serial/steps
```

### Batch Analytics
```
GET /api/batch/:batchNumber/summary
GET /api/batch/:batchNumber/yield
GET /api/batch/:batchNumber/station-stats
```

### Machine Analytics
```
GET /api/machine/:machineId/telemetry
GET /api/machine/:machineId/ml-results
GET /api/machine/:machineId/alerts
```

### Health Check
```
GET /health
GET /health/detailed
```

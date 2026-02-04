# UDT Structures for TIA Portal Integration

This document describes the PLC data structures that need to be created in TIA Portal for IIoT integration.

## DB50 - Telemetry Data

```scl
DATA_BLOCK "DB_IoT_Telemetry"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0
VAR
    // Vibration sensors
    RealVibrationX : Real;    // X-axis vibration (mm/s)
    RealVibrationY : Real;    // Y-axis vibration (mm/s)
    RealVibrationZ : Real;    // Z-axis vibration (mm/s)
    
    // Temperature sensors
    RealTempMotor : Real;     // Motor temperature (°C)
    RealTempAmbient : Real;   // Ambient temperature (°C)
    RealTempHydraulic : Real; // Hydraulic oil temperature (°C)
    
    // Counters
    CounterCycles : DInt;     // Total cycle count
    CounterHours : Real;      // Operating hours
    
    // Status flags
    BoolRunning : Bool;       // Machine running status
    BoolAlarm : Bool;         // Alarm status
    BoolEmergencyStop : Bool; // Emergency stop status
    
    // Timestamp (synced from NTP or PLC clock)
    LDT_Timestamp : LDT;      // Local date and time
    
    // Reserved for future expansion
    Reserved : ARRAY[1..10] OF Real;
END_VAR
BEGIN
END_DATA_BLOCK
```

## DB100 - Product Tracking Header

```scl
DATA_BLOCK "DB_Product_Header"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0
VAR
    // Product identification
    stHeader : STRUCT
        uiProductId : UDINT;           // Internal product ID
        sProductUUID : STRING[36];     // UUID for traceability
        sSerialNumber : STRING[50];    // Serial number
        sBatchNumber : STRING[50];     // Batch number
        sMaterialBatch : STRING[50];   // Material batch
        uiProductType : UINT;          // Product type reference
        uiVariant : UINT;              // Variant reference
        uiCustomerId : UINT;           // Customer reference
        sWorkOrderId : STRING[30];     // Work order ID
        
        // Timestamps
        ldtCreated : LDT;              // Creation timestamp
        ldtStarted : LDT;              // Start processing
        ldtCompleted : LDT;            // Completion timestamp
        
        // Status
        eStatus : INT;                 // 0=Created, 1=InProgress, 2=Completed, 3=Rejected
        eQualityResult : INT;          // 0=Pending, 1=OK, 2=NG, 3=Rework
        uiQuantity : UINT;             // Quantity
    END_STRUCT;
    
    // Process steps array
    stSteps : ARRAY[1..20] OF STRUCT
        uiStepNumber : UINT;           // Step number
        sStepName : STRING[50];        // Step name
        sStationId : STRING[20];       // Station ID
        sPositionId : STRING[20];      // Position ID
        
        ldtEntryTime : LDT;            // Entry timestamp
        ldtExitTime : LDT;             // Exit timestamp
        uiTotalTimeMs : UDINT;         // Total time in ms
        
        eStepStatus : INT;             // 0=Pending, 1=Running, 2=Completed, 3=Skipped, 4=Error
        eStepResult : INT;             // 0=Unknown, 1=Pass, 2=Fail
        
        uiCycleCount : UDINT;          // Cycle count at this step
        rCycleTimeAvg : Real;          // Average cycle time
        rCycleTimeMin : Real;          // Min cycle time
        rCycleTimeMax : Real;          // Max cycle time
        
        uiErrorCode : UINT;            // Error code if failed
        sErrorDescription : STRING[200]; // Error description
        uiRetryCount : UINT;           // Retry count
    END_STRUCT;
    
    // Current active product
    stCurrentProduct : STRUCT
        sSerialNumber : STRING[50];
        bActive : Bool;
        uiCurrentStep : UINT;
    END_STRUCT;
END_VAR
BEGIN
END_DATA_BLOCK
```

## DB150 - Measurement Results

```scl
DATA_BLOCK "DB_Measurement_Results"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0
VAR
    // Current measurement
    stCurrentMeasurement : STRUCT
        uiMeasurementId : UDINT;
        sSerialNumber : STRING[50];
        sMeasurementName : STRING[50];
        sUnit : STRING[10];
        
        rValue : Real;
        rMinLimit : Real;
        rMaxLimit : Real;
        rTarget : Real;
        rTolerance : Real;
        
        rAverage : Real;
        rStdDev : Real;
        rMin : Real;
        rMax : Real;
        uiSampleCount : UINT;
        
        bIsPass : Bool;
        rDeviation : Real;
        rCpk : Real;
        
        ldtTimestamp : LDT;
        sStationId : STRING[20];
        sSensorId : STRING[20];
    END_STRUCT;
    
    // Measurement buffer (for batch uploads)
    stMeasurementBuffer : ARRAY[1..100] OF STRUCT
        sSerialNumber : STRING[50];
        sMeasurementName : STRING[50];
        rValue : Real;
        rMinLimit : Real;
        rMaxLimit : Real;
        ldtTimestamp : LDT;
        sStationId : STRING[20];
    END_STRUCT;
    
    uiBufferCount : UINT;
    uiBufferIndex : UINT;
END_VAR
BEGIN
END_DATA_BLOCK
```

## DB200 - ML Results

```scl
DATA_BLOCK "DB_ML_Results"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0
VAR
    // Anomaly detection
    bAnomalyDetected : Bool;
    rAnomalyProbability : Real;
    rAnomalyThreshold : Real := 0.7;
    
    // RUL Prediction
    rRUL_Days : Real;
    rRUL_ThresholdWarning : Real := 30.0;
    rRUL_ThresholdCritical : Real := 7.0;
    eRULStatus : INT;                 // 0=Normal, 1=Warning, 2=Critical
    
    // Feature summary
    rVibrationRMS : Real;
    rTemperatureAvg : Real;
    rCycleTimeAvg : Real;
    
    // Last update
    ldtLastUpdate : LDT;
    
    // Model status
    eModelStatus : INT;               // 0=Idle, 1=Running, 2=Error
    sModelVersion : STRING[20];
END_VAR
BEGIN
END_DATA_BLOCK
```

## OPC UA Server Configuration

### Export XML Structure

The UDTs above should be exported from TIA Portal as XML and used for OPC UA server configuration. The following nodes will be exposed:

```
Objects
├── NodeId: ns=2;s=DB50
│   ├── RealVibrationX (Real)
│   ├── RealVibrationY (Real)
│   ├── RealVibrationZ (Real)
│   ├── RealTempMotor (Real)
│   ├── RealTempAmbient (Real)
│   ├── RealTempHydraulic (Real)
│   ├── CounterCycles (DInt)
│   ├── CounterHours (Real)
│   ├── BoolRunning (Bool)
│   ├── BoolAlarm (Bool)
│   └── LDT_Timestamp (LDateTime)
│
├── NodeId: ns=2;s=DB100
│   ├── stHeader
│   │   ├── sSerialNumber (String)
│   │   ├── sBatchNumber (String)
│   │   └── ... (other fields)
│   ├── stSteps[1..20]
│   └── stCurrentProduct
│
├── NodeId: ns=2;s=DB150
│   └── stCurrentMeasurement
│
└── NodeId: ns=2;s=DB200
    ├── bAnomalyDetected (Bool)
    ├── rAnomalyProbability (Real)
    └── rRUL_Days (Real)
```

## MQTT Topic Mapping

| DB | Node | MQTT Topic |
|----|------|------------|
| DB50 | All telemetry | `op10/telemetry/{node_id}` |
| DB100 | Product events | `op10/product/{event}` |
| DB150 | Measurements | `op10/product/measurement` |
| DB200 | ML results | `op10/ml/results` |

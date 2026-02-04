# ML Models for OP10 IIoT Platform

This directory contains trained ML models in ONNX format for edge inference.

## Model Files

| Model | File | Description |
|-------|------|-------------|
| Anomaly Detection | `anomaly_detector.onnx` | Isolation Forest for anomaly detection |
| RUL Prediction | `rul_predictor.onnx` | Remaining Useful Life prediction |

## Model Training Pipeline

### 1. Data Collection

Collect at least 30 days of normal operation data:
- Vibration data (X, Y, Z axes)
- Temperature data (motor, ambient, hydraulic)
- Cycle counts and operating hours

### 2. Feature Engineering

Features are extracted using `services/ml-inference/feature_extraction.py`:

```python
# Vibration features (per axis)
- RMS value
- Peak value
- Crest factor
- Kurtosis
- Dominant frequency
- Spectral centroid
- Low/high frequency ratio

# Temperature features
- Mean temperature
- Temperature gradient
- Rate of change

# Cycle features
- Average cycle time
- Cycle time variance
```

### 3. Training

```bash
# Train anomaly detection model
python train_anomaly_model.py --data ./data/normal_data.csv --output ./models/anomaly_detector.onnx

# Train RUL prediction model
python train_rul_model.py --data ./data/historical_data.csv --output ./models/rul_predictor.onnx
```

### 4. Conversion to ONNX

```python
import onnx
from sklearn.ensemble import IsolationForest
import skl2onnx

# Train model
model = IsolationForest(n_estimators=100, contamination=0.1)
model.fit(X_train)

# Convert to ONNX
initial_type = [('float_input', FloatTensorType([None, 15]))]
onnx_model = skl2onnx.convert_sklearn(model, initial_types=initial_type)

# Save
with open('./models/anomaly_detector.onnx', 'wb') as f:
    f.write(onnx_model.SerializeToString())
```

## Model Performance

### Anomaly Detection Model
- **Algorithm:** Isolation Forest
- **Input Features:** 15 features
- **Output:** Anomaly probability (0-1)
- **Threshold:** 0.7 (configurable)
- **Expected Performance:**
  - Precision: > 0.85
  - Recall: > 0.80
  - F1-Score: > 0.82

### RUL Prediction Model
- **Algorithm:** Gradient Boosting Regressor
- **Input Features:** 15 features
- **Output:** Days until maintenance (0-365)
- **Expected MAE:** < 5 days

## Model Monitoring

Track model performance using Grafana dashboard:
- Prediction distribution
- False positive rate
- Feature drift detection

## Model Updates

To update models with new data:

1. Collect new labeled data (normal vs. anomaly cases)
2. Retrain models with increased dataset
3. Test on validation set
4. Deploy to edge devices
5. Monitor for performance degradation

## Model Versioning

Use semantic versioning:
- Major: Architecture changes
- Minor: New features
- Patch: Bug fixes, performance improvements

Store model metadata in `models/metadata.json`:
```json
{
    "anomaly_detector": {
        "version": "1.0.0",
        "trained_at": "2024-02-02T14:30:00Z",
        "training_samples": 45000,
        "accuracy": 0.87,
        "algorithm": "IsolationForest",
        "parameters": {
            "n_estimators": 100,
            "contamination": 0.1
        }
    },
    "rul_predictor": {
        "version": "1.0.0",
        "trained_at": "2024-02-02T14:30:00Z",
        "training_samples": 12000,
        "mae": 4.2,
        "algorithm": "GradientBoosting",
        "parameters": {
            "n_estimators": 100,
            "learning_rate": 0.1
        }
    }
}
```

## Placeholder Models

Since no historical data is available yet, placeholder models are provided that:
- Return random predictions for testing
- Accept the correct input shape
- Allow integration testing

To use placeholder models:
1. Place `anomaly_detector.onnx` in this directory
2. Place `rul_predictor.onnx` in this directory
3. Models will be loaded automatically on service start

## Input/Output Specifications

### Anomaly Detector Input
| Name | Type | Shape | Description |
|------|------|-------|-------------|
| float_input | float32 | [1, 15] | Feature vector |

### Anomaly Detector Output
| Name | Type | Shape | Description |
|------|------|-------|-------------|
| output | float32 | [1, 2] | [normal_prob, anomaly_prob] |

### RUL Predictor Input
| Name | Type | Shape | Description |
|------|------|-------|-------------|
| float_input | float32 | [1, 15] | Feature vector |

### RUL Predictor Output
| Name | Type | Shape | Description |
|------|------|-------|-------------|
| output | float32 | [1, 1] | Days remaining |

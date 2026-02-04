#!/usr/bin/env python3
"""
ML Inference Service for OP10 IIoT Platform
Anomaly detection and RUL prediction using ONNX models
"""

import asyncio
import json
import logging
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import onnxruntime as ort
import redis
import yaml
from paho.mqtt import client as mqtt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self, broker: str, port: int, user: Optional[str] = None, password: Optional[str] = None):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        if user and password:
            self.client.username_pw_set(user, password)
        self.client.connect(broker, port, 60)
        self.client.loop_start()
        logger.info(f"MQTT connected to {broker}:{port}")

    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 1):
        try:
            result = self.client.publish(topic, json.dumps(payload), qos)
            return result
        except Exception as e:
            logger.error(f"MQTT publish error: {e}")
            return None

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


class FeatureExtractor:
    """Extract features from raw telemetry data"""

    @staticmethod
    def extract_vibration_features(values: np.ndarray, sampling_rate: float = 1000.0) -> Dict[str, float]:
        if len(values) < 10:
            return {}

        features = {}

        rms = np.sqrt(np.mean(values ** 2))
        features['rms'] = float(rms)

        peak = np.max(np.abs(values))
        features['peak'] = float(peak)
        features['crest_factor'] = float(peak / rms) if rms > 0 else 0

        features['kurtosis'] = float(np.mean(((values - np.mean(values)) / np.std(values)) ** 4))
        features['skewness'] = float(np.mean(((values - np.mean(values)) / np.std(values)) ** 3))

        fft = np.fft.fft(values)
        freqs = np.fft.fftfreq(len(values), 1 / sampling_rate)

        pos_mask = freqs > 0
        pos_freqs = freqs[pos_mask]
        pos_fft = np.abs(fft)[pos_mask]

        dominant_idx = np.argmax(pos_fft)
        features['dominant_frequency'] = float(pos_freqs[dominant_idx])
        features['spectral_centroid'] = float(np.sum(pos_freqs * pos_fft) / np.sum(pos_fft))

        low_band = np.sum(pos_fft[(pos_freqs >= 0) & (pos_freqs < 100)])
        mid_band = np.sum(pos_fft[(pos_freqs >= 100) & (pos_freqs < 1000)])
        high_band = np.sum(pos_fft[(pos_freqs >= 1000) & (pos_freqs < 5000)])
        features['low_high_ratio'] = float(low_band / high_band) if high_band > 0 else 0

        return features

    @staticmethod
    def extract_temperature_features(values: List[float], timestamps: List[float]) -> Dict[str, float]:
        if len(values) < 2:
            return {}

        arr = np.array(values)
        features = {}

        features['mean'] = float(np.mean(arr))
        features['std'] = float(np.std(arr))
        features['min'] = float(np.min(arr))
        features['max'] = float(np.max(arr))

        if len(values) > 1:
            gradient = np.gradient(arr, np.diff(timestamps) if len(timestamps) > 1 else None)
            features['gradient'] = float(np.mean(gradient))

        features['rate_of_change'] = float((arr[-1] - arr[0]) / (len(arr) * 0.1))

        return features

    @staticmethod
    def create_feature_vector(
        vibration_x: np.ndarray,
        vibration_y: np.ndarray,
        vibration_z: np.ndarray,
        temperature: List[float],
        cycles: List[float]
    ) -> np.ndarray:
        features = []

        for axis_name, data in [('x', vibration_x), ('y', vibration_y), ('z', vibration_z)]:
            feats = FeatureExtractor.extract_vibration_features(data)
            features.extend([
                feats.get('rms', 0),
                feats.get('peak', 0),
                feats.get('crest_factor', 0),
                feats.get('kurtosis', 0),
                feats.get('dominant_frequency', 0),
            ])

        temp_feats = FeatureExtractor.extract_temperature_features(temperature, list(range(len(temperature))))
        features.extend([
            temp_feats.get('mean', 0),
            temp_feats.get('gradient', 0),
            temp_feats.get('rate_of_change', 0),
        ])

        if len(cycles) > 0:
            features.append(float(np.mean(cycles)))
            features.append(float(np.std(cycles)) if len(cycles) > 1 else 0)
        else:
            features.extend([0, 0])

        return np.array(features, dtype=np.float32)


class MLInference:
    def __init__(self, model_path: str, rul_model_path: Optional[str] = None):
        self.model_path = Path(model_path)
        self.rul_model_path = Path(rul_model_path) if rul_model_path else None

        self.session = ort.InferenceSession(
            str(self.model_path),
            providers=['CPUExecutionProvider']
        )

        if self.rul_model_path and self.rul_model_path.exists():
            self.rul_session = ort.InferenceSession(
                str(self.rul_model_path),
                providers=['CPUExecutionProvider']
            )
        else:
            self.rul_session = None

        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        logger.info(f"ML model loaded: {self.model_path}")
        logger.info(f"RUL model loaded: {self.rul_model_path}")

    def predict_anomaly(self, features: np.ndarray) -> Tuple[int, float]:
        input_data = np.expand_dims(features, axis=0)
        input_data = np.nan_to_num(input_data, nan=0.0, posinf=1.0, neginf=-1.0)

        prediction = self.session.run([self.output_name], {self.input_name: input_data})[0]
        probability = float(prediction[0][1])

        anomaly = 1 if probability > 0.7 else 0
        return anomaly, probability

    def predict_rul(self, features: np.ndarray) -> Optional[float]:
        if not self.rul_session:
            return None

        input_data = np.expand_dims(features, axis=0)
        input_data = np.nan_to_num(input_data, nan=0.0, posinf=1.0, neginf=-1.0)

        try:
            output = self.rul_session.run(None, {self.input_name: input_data})[0]
            rul = float(output[0][0])
            return max(0, min(rul, 365))
        except Exception as e:
            logger.error(f"RUL prediction error: {e}")
            return None


class RedisBuffer:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.buffer_keys = {
            'vibration_x': 'op10:buffer:vibration:x',
            'vibration_y': 'op10:buffer:vibration:y',
            'vibration_z': 'op10:buffer:vibration:z',
            'temperature': 'op10:buffer:temperature',
            'cycles': 'op10:buffer:cycles',
        }
        self.buffer_size = 1000

    def add_telemetry(self, node_id: str, value: float, timestamp: float):
        key = None
        for pattern, buffer_key in self.buffer_keys.items():
            if pattern in node_id.lower():
                key = buffer_key
                break

        if not key:
            return

        data = json.dumps({'value': value, 'timestamp': timestamp})
        pipe = self.redis.pipeline()
        pipe.rpush(key, data)
        pipe.ltrim(key, -self.buffer_size, -1)
        pipe.execute()

    def get_buffer(self, key_name: str) -> Tuple[List[float], List[float]]:
        key = self.buffer_keys.get(key_name)
        if not key:
            return [], []

        data = self.redis.lrange(key, 0, -1)
        values = []
        timestamps = []
        for item in data:
            parsed = json.loads(item)
            values.append(parsed['value'])
            timestamps.append(parsed['timestamp'])

        return values, timestamps


class MLService:
    def __init__(self, config_path: str = "/config/ml_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.redis_buffer = RedisBuffer(self.config.get('redis_url', 'redis://redis:6379'))
        self.mqtt_client = self.init_mqtt()

        model_path = self.config.get('model_path', '/models/anomaly_detector.onnx')
        rul_model_path = self.config.get('rul_model_path', None)

        self.ml_inference = MLInference(model_path, rul_model_path)
        self.extractor = FeatureExtractor()
        self.running = False

    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            'mqtt': {
                'broker': 'mosquitto',
                'port': 1883
            },
            'redis_url': 'redis://redis:6379',
            'model_path': '/models/anomaly_detector.onnx',
            'rul_model_path': '/models/rul_predictor.onnx',
            'inference_interval': 5.0
        }

    def init_mqtt(self) -> MQTTClient:
        mqtt_cfg = self.config.get('mqtt', {})
        return MQTTClient(
            broker=mqtt_cfg.get('broker', 'mosquitto'),
            port=mqtt_cfg.get('port', 1883)
        )

    def process_telemetry(self, topic: str, payload: Dict[str, Any]):
        node_id = payload.get('node_id', '')
        value = payload.get('value', 0)
        timestamp = payload.get('timestamp', datetime.utcnow().timestamp())

        self.redis_buffer.add_telemetry(node_id, value, timestamp)

    async def run_inference(self):
        while self.running:
            try:
                vib_x, _ = self.redis_buffer.get_buffer('vibration_x')
                vib_y, _ = self.redis_buffer.get_buffer('vibration_y')
                vib_z, _ = self.redis_buffer.get_buffer('vibration_z')
                temp, _ = self.redis_buffer.get_buffer('temperature')
                cycles, _ = self.redis_buffer.get_buffer('cycles')

                if len(vib_x) < 100:
                    await asyncio.sleep(1)
                    continue

                features = self.extractor.create_feature_vector(
                    np.array(vib_x[-1000:]),
                    np.array(vib_y[-1000:]),
                    np.array(vib_z[-1000:]),
                    temp[-60:],
                    cycles[-60:]
                )

                anomaly, probability = self.ml_inference.predict_anomaly(features)
                rul = self.ml_inference.predict_rul(features)

                result = {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'anomaly': anomaly,
                    'probability': probability,
                    'rul_days': rul,
                    'features_summary': {
                        'rms_x': float(np.sqrt(np.mean(np.array(vib_x[-1000:]) ** 2))),
                        'rms_y': float(np.sqrt(np.mean(np.array(vib_y[-1000:]) ** 2))),
                        'rms_z': float(np.sqrt(np.mean(np.array(vib_z[-1000:]) ** 2))),
                        'temp_avg': float(np.mean(temp[-60:])) if temp else 0,
                    }
                }

                self.mqtt_client.publish('op10/ml/results', result)

                if anomaly:
                    self.mqtt_client.publish('op10/alerts/anomaly', {
                        'timestamp': result['timestamp'],
                        'probability': probability,
                        'rul_days': rul
                    })

            except Exception as e:
                logger.error(f"Inference error: {e}")

            await asyncio.sleep(self.config.get('inference_interval', 5.0))

    async def run(self):
        self.running = True
        logger.info("ML Inference service started")

        inference_task = asyncio.create_task(self.run_inference())

        while self.running:
            await asyncio.sleep(1)

        inference_task.cancel()
        logger.info("ML Inference service stopped")

    def stop(self):
        self.running = False
        self.mqtt_client.disconnect()


def create_default_config():
    config = {
        'mqtt': {
            'broker': 'mosquitto',
            'port': 1883
        },
        'redis_url': 'redis://redis:6379',
        'model_path': '/models/anomaly_detector.onnx',
        'rul_model_path': '/models/rul_predictor.onnx',
        'inference_interval': 5.0,
        'thresholds': {
            'anomaly_probability': 0.7,
            'rul_warning_days': 30,
            'rul_critical_days': 7
        },
        'features': {
            'vibration_window': 1000,
            'temperature_window': 60,
            'cycles_window': 60
        }
    }

    config_path = Path("/config/ml_config.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    logger.info(f"Default ML config created at {config_path}")


def main():
    import os

    if os.environ.get("CREATE_ML_CONFIG"):
        create_default_config()

    service = MLService()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        service.stop()
        loop.call_soon_threadsafe(loop.stop)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        loop.run_until_complete(service.run())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
    finally:
        loop.close()


if __name__ == "__main__":
    main()

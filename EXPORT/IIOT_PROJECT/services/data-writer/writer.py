#!/usr/bin/env python3
"""
Data Writer Service for OP10 IIoT Platform
Writes telemetry data to InfluxDB and PostgreSQL
"""

import asyncio
import json
import logging
import signal
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
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

    def subscribe(self, topic: str, callback):
        self.client.message_callback_add(topic, callback)
        self.client.subscribe(topic)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


class InfluxWriter:
    def __init__(self, url: str, org: str, token: str, bucket: str):
        self.client = InfluxDBClient(url=url, org=org, token=token)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.bucket = bucket
        self.org = org
        logger.info(f"InfluxDB connected: {url}")

    def write_telemetry(self, topic: str, payload: Dict[str, Any]):
        try:
            timestamp = payload.get('timestamp', datetime.utcnow().isoformat() + 'Z')
            node_id = payload.get('node_id', 'unknown')
            value = payload.get('value', 0)

            tags = {
                'machine_id': 'OP10',
                'station': 'OP010'
            }

            fields = {
                'value': float(value),
                'node_id': node_id
            }

            if 'quality' in payload:
                fields['quality'] = payload['quality']

            point = Point("telemetry") \
                .tag('machine_id', 'OP10') \
                .tag('node_id', node_id) \
                .field('value', float(value)) \
                .time(timestamp)

            self.write_api.write(bucket=self.bucket, org=self.org, record=point)

        except Exception as e:
            logger.error(f"InfluxDB write error: {e}")

    def write_product_timing(self, product_id: str, step_name: str,
                             duration_ms: int, station_id: str):
        try:
            point = Point("product_timing") \
                .tag('product_id', product_id) \
                .tag('station_id', station_id) \
                .tag('step_name', step_name) \
                .field('duration_ms', duration_ms) \
                .time(datetime.utcnow())

            self.write_api.write(bucket=self.bucket, org=self.org, record=point)

        except Exception as e:
            logger.error(f"InfluxDB write error: {e}")

    def write_quality_yield(self, station_id: str, product_type: str,
                            pass_count: int, fail_count: int):
        try:
            total = pass_count + fail_count
            yield_pct = (pass_count / total * 100) if total > 0 else 0

            point = Point("quality_yield") \
                .tag('station_id', station_id) \
                .tag('product_type', product_type) \
                .field('pass_count', pass_count) \
                .field('fail_count', fail_count) \
                .field('yield_percent', yield_pct) \
                .field('total_count', total) \
                .time(datetime.utcnow())

            self.write_api.write(bucket=self.bucket, org=self.org, record=point)

        except Exception as e:
            logger.error(f"InfluxDB write error: {e}")

    def close(self):
        self.client.close()


class DataWriter:
    def __init__(self, config_path: str = "/config/writer_config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()

        influx_cfg = self.config.get('influx', {})
        self.influx_writer = InfluxWriter(
            url=influx_cfg.get('url', 'http://influxdb:8086'),
            org=influx_cfg.get('org', 'op10'),
            token=influx_cfg.get('token', 'op10-super-secret-token'),
            bucket=influx_cfg.get('bucket', 'telemetry')
        )

        mqtt_cfg = self.config.get('mqtt', {})
        self.mqtt_client = MQTTClient(
            broker=mqtt_cfg.get('broker', 'mosquitto'),
            port=mqtt_cfg.get('port', 1883)
        )

        self.running = False

    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            'influx': {
                'url': 'http://influxdb:8086',
                'org': 'op10',
                'token': 'op10-super-secret-token',
                'bucket': 'telemetry'
            },
            'mqtt': {
                'broker': 'mosquitto',
                'port': 1883
            }
        }

    def handle_telemetry(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            self.influx_writer.write_telemetry(msg.topic, payload)
        except Exception as e:
            logger.error(f"Telemetry processing error: {e}")

    def handle_product_timing(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            self.influx_writer.write_product_timing(
                product_id=payload.get('product_id'),
                step_name=payload.get('step_name'),
                duration_ms=payload.get('duration_ms', 0),
                station_id=payload.get('station_id', 'unknown')
            )
        except Exception as e:
            logger.error(f"Product timing error: {e}")

    def handle_quality(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            self.influx_writer.write_quality_yield(
                station_id=payload.get('station_id'),
                product_type=payload.get('product_type'),
                pass_count=payload.get('pass_count', 0),
                fail_count=payload.get('fail_count', 0)
            )
        except Exception as e:
            logger.error(f"Quality data error: {e}")

    def setup_subscriptions(self):
        self.mqtt_client.subscribe('op10/telemetry/#', self.handle_telemetry)
        self.mqtt_client.subscribe('op10/product/timing', self.handle_product_timing)
        self.mqtt_client.subscribe('op10/quality/yield', self.handle_quality)
        logger.info("Data writer subscriptions set up")

    def run(self):
        self.running = True
        self.setup_subscriptions()
        logger.info("Data writer service started")

        try:
            while self.running:
                asyncio.run(asyncio.sleep(1))
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        self.influx_writer.close()
        self.mqtt_client.disconnect()
        logger.info("Data writer service stopped")


def create_default_config():
    config = {
        'influx': {
            'url': 'http://influxdb:8086',
            'org': 'op10',
            'token': 'op10-super-secret-token',
            'bucket': 'telemetry'
        },
        'mqtt': {
            'broker': 'mosquitto',
            'port': 1883
        },
        'batch_size': 1000,
        'flush_interval': 10
    }

    config_path = Path("/config/writer_config.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    logger.info(f"Default writer config created at {config_path}")


def main():
    import os
    from pathlib import Path

    if os.environ.get("CREATE_WRITER_CONFIG"):
        create_default_config()

    writer = DataWriter()
    writer.run()


if __name__ == "__main__":
    main()

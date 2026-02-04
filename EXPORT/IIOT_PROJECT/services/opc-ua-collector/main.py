#!/usr/bin/env python3
"""
OPC UA Collector Service for OP10 IIoT Platform
Subscribes to PLC data and publishes to MQTT broker
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import yaml
from asyncua import Client, Subscription, ua
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
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.warning(f"MQTT publish failed: {mqtt.error_string(result.rc)}")
            return result
        except Exception as e:
            logger.error(f"MQTT publish error: {e}")
            return None

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


class SubHandler:
    def __init__(self, mqtt_client: MQTTClient):
        self.mqtt_client = mqtt_client
        self.data_buffer: Dict[str, List[Dict]] = {}

    def datachange_notification(self, node: ua.Node, value: Any, data: ua.DataChangeNotification):
        try:
            node_id = node.nodeid.to_string()
            topic = f"op10/telemetry/{node_id.replace(':', '_').replace('.', '_')}"
            payload = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "node_id": node_id,
                "value": float(value) if isinstance(value, (int, float)) else value,
                "quality": str(data.monitored_items[0].status.Value)
            }
            self.mqtt_client.publish(topic, payload)
        except Exception as e:
            logger.error(f"Data change notification error: {e}")

    def event_notification(self, event: ua.EventFieldList):
        logger.debug(f"Event received: {event}")


class OPCUACollector:
    def __init__(self, config_path: str = "/config/config.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.mqtt_client = self.init_mqtt()
        self.client = None
        self.subscription = None
        self.handler = None
        self.running = False

    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            "plc": {
                "endpoint": "opc.tcp://192.168.1.100:4840",
                "user": None,
                "password": None
            },
            "mqtt": {
                "broker": "mosquitto",
                "port": 1883,
                "user": None,
                "password": None
            },
            "collection": {
                "interval_ms": 100,
                "nodes": []
            }
        }

    def init_mqtt(self) -> MQTTClient:
        mqtt_cfg = self.config.get("mqtt", {})
        return MQTTClient(
            broker=mqtt_cfg.get("broker", "mosquitto"),
            port=mqtt_cfg.get("port", 1883),
            user=mqtt_cfg.get("user"),
            password=mqtt_cfg.get("password")
        )

    def get_node_path(self, node_string: str) -> str:
        mapping = {
            "vibration": "DB50",
            "temperature": "DB50",
            "cycles": "DB50",
            "product": "DB100"
        }
        for key, db in mapping.items():
            if db in node_string:
                return f"op10/{key}"
        return "op10/telemetry"

    async def connect(self):
        plc_cfg = self.config.get("plc", {})
        endpoint = plc_cfg.get("endpoint", "opc.tcp://192.168.1.100:4840")
        user = plc_cfg.get("user")
        password = plc_cfg.get("password")

        logger.info(f"Connecting to PLC: {endpoint}")
        self.client = Client(url=endpoint)

        if user and password:
            self.client.set_user_token(user, password)

        await self.client.connect()
        logger.info("OPC UA connected")

        root = self.client.get_root_node()
        objects = await root.get_child("0:Objects")

        self.handler = SubHandler(self.mqtt_client)
        self.subscription = await self.client.create_subscription(
            self.config.get("collection", {}).get("interval_ms", 100),
            self.handler
        )
        logger.info("Subscription created")

    async def subscribe_nodes(self, nodes: List[str]):
        if not self.subscription or not self.client:
            raise RuntimeError("Not connected to PLC")

        for node_path in nodes:
            try:
                node = await self.client.get_node(node_path)
                await self.subscription.subscribe_data_change(node)
                logger.info(f"Subscribed to: {node_path}")
            except Exception as e:
                logger.error(f"Failed to subscribe {node_path}: {e}")

    async def subscribe_default_nodes(self):
        default_nodes = [
            "ns=2;s=DB50.RealVibrationX",
            "ns=2;s=DB50.RealVibrationY",
            "ns=2;s=DB50.RealVibrationZ",
            "ns=2;s=DB50.RealTempMotor",
            "ns=2;s=DB50.RealTempAmbient",
            "ns=2;s=DB50.RealTempHydraulic",
            "ns=2;s=DB50.CounterCycles",
            "ns=2;s=DB50.CounterHours",
            "ns=2;s=DB50.BoolRunning",
            "ns=2;s=DB50.BoolAlarm",
        ]
        await self.subscribe_nodes(default_nodes)

    async def run(self):
        self.running = True

        try:
            await self.connect()
            nodes = self.config.get("collection", {}).get("nodes", [])
            if nodes:
                await self.subscribe_nodes(nodes)
            else:
                await self.subscribe_default_nodes()

            while self.running:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info("Received cancellation signal")
        except Exception as e:
            logger.error(f"Runtime error: {e}")
        finally:
            await self.disconnect()

    async def disconnect(self):
        self.running = False
        if self.subscription:
            await self.subscription.delete()
        if self.client:
            await self.client.disconnect()
        self.mqtt_client.disconnect()
        logger.info("Disconnected from PLC and MQTT")

    def stop(self):
        self.running = False


def create_default_config():
    config = {
        "plc": {
            "endpoint": "opc.tcp://192.168.1.100:4840",
            "user": None,
            "password": None
        },
        "mqtt": {
            "broker": "mosquitto",
            "port": 1883,
            "user": None,
            "password": None
        },
        "collection": {
            "interval_ms": 100,
            "nodes": []
        },
        "telemetry": {
            "vibration": {
                "enabled": True,
                "nodes": [
                    "ns=2;s=DB50.RealVibrationX",
                    "ns=2;s=DB50.RealVibrationY",
                    "ns=2;s=DB50.RealVibrationZ"
                ]
            },
            "temperature": {
                "enabled": True,
                "nodes": [
                    "ns=2;s=DB50.RealTempMotor",
                    "ns=2;s=DB50.RealTempAmbient",
                    "ns=2;s=DB50.RealTempHydraulic"
                ]
            },
            "cycles": {
                "enabled": True,
                "nodes": [
                    "ns=2;s=DB50.CounterCycles",
                    "ns=2;s=DB50.CounterHours"
                ]
            },
            "status": {
                "enabled": True,
                "nodes": [
                    "ns=2;s=DB50.BoolRunning",
                    "ns=2;s=DB50.BoolAlarm"
                ]
            }
        }
    }

    config_path = Path("/config/config.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    logger.info(f"Default config created at {config_path}")


def main():
    import os

    if os.environ.get("CREATE_DEFAULT_CONFIG"):
        create_default_config()

    collector = OPCUACollector()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def signal_handler(sig, frame):
        logger.info("Shutdown signal received")
        collector.stop()
        loop.call_soon_threadsafe(loop.stop)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        loop.run_until_complete(collector.run())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
    finally:
        loop.close()
        logger.info("Collector stopped")


if __name__ == "__main__":
    main()

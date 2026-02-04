#!/usr/bin/env python3
"""
Product Tracking Service for OP10 IIoT Platform
Tracks product history through manufacturing process
"""

import asyncio
import json
import logging
import signal
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import asynccontextmanager

import yaml
from paho.mqtt import client as mqtt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

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

    def subscribe(self, topic: str, callback):
        self.client.message_callback_add(topic, callback)
        self.client.subscribe(topic)
        logger.info(f"Subscribed to {topic}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()


class ProductDatabase:
    def __init__(self, db_url: str):
        self.engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600
        )
        self.SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

    def get_session(self):
        return self.SessionLocal()

    @asynccontextmanager
    def session_scope(self):
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_product(self, serial_number: str, batch_number: Optional[str] = None,
                       product_type_id: Optional[int] = None, variant_id: Optional[int] = None,
                       customer_id: Optional[int] = None, work_order_id: Optional[str] = None,
                       metadata: Optional[Dict] = None) -> str:
        with self.session_scope() as session:
            query = text("""
                INSERT INTO products (serial_number, batch_number, product_type_id, variant_id,
                                     customer_id, work_order_id, status, metadata)
                VALUES (:serial, :batch, :type_id, :variant, :cust_id, :wo, 'in_progress', :meta)
                RETURNING id
            """)
            result = session.execute(query, {
                'serial': serial_number,
                'batch': batch_number,
                'type_id': product_type_id,
                'variant': variant_id,
                'cust_id': customer_id,
                'wo': work_order_id,
                'meta': json.dumps(metadata or {})
            })
            product_id = result.fetchone()[0]
            logger.info(f"Product created: {serial_number} ({product_id})")
            return str(product_id)

    def update_product_status(self, serial_number: str, status: str, quality_result: Optional[str] = None):
        with self.session_scope() as session:
            updates = {'status': status}
            if quality_result:
                updates['quality_result'] = quality_result
            if status in ('completed', 'rejected'):
                updates['completed_at'] = datetime.utcnow()

            query = text("""
                UPDATE products SET status = :status, quality_result = :quality,
                    completed_at = :completed
                WHERE serial_number = :serial
            """)
            session.execute(query, {
                'serial': serial_number,
                'status': status,
                'quality': quality_result,
                'completed': datetime.utcnow() if status in ('completed', 'rejected') else None
            })

    def log_process_step(self, product_id: str, step_number: int, step_name: str,
                         station_id: str, position_id: Optional[str] = None,
                         entry_time: Optional[datetime] = None, exit_time: Optional[datetime] = None,
                         step_status: str = 'completed', step_result: Optional[str] = None,
                         cycle_count: Optional[int] = None, error_code: Optional[int] = None,
                         error_description: Optional[str] = None):
        with self.session_scope() as session:
            processing_time = None
            if entry_time and exit_time:
                processing_time = int((exit_time - entry_time).total_seconds() * 1000)

            query = text("""
                INSERT INTO process_steps (product_id, step_number, step_name, station_id, position_id,
                                          entry_time, exit_time, processing_duration_ms, step_status,
                                          step_result, cycle_count, error_code, error_description)
                VALUES (:prod_id, :step_num, :step_name, :station, :pos, :entry, :exit, :duration,
                        :status, :result, :cycles, :err_code, :err_desc)
                ON CONFLICT (product_id, step_number) DO UPDATE SET
                    exit_time = :exit,
                    processing_duration_ms = :duration,
                    step_status = :status,
                    step_result = :result,
                    cycle_count = :cycles,
                    error_code = :err_code,
                    error_description = :err_desc
            """)
            session.execute(query, {
                'prod_id': product_id,
                'step_num': step_number,
                'step_name': step_name,
                'station': station_id,
                'pos': position_id,
                'entry': entry_time or datetime.utcnow(),
                'exit': exit_time or datetime.utcnow(),
                'duration': processing_time,
                'status': step_status,
                'result': step_result,
                'cycles': cycle_count,
                'err_code': error_code,
                'err_desc': error_description
            })
            logger.info(f"Process step logged: {product_id} - {step_name}")

    def log_measurement(self, product_id: str, step_id: Optional[int], measurement_name: str,
                        value: float, unit: Optional[str] = None,
                        min_limit: Optional[float] = None, max_limit: Optional[float] = None,
                        target_value: Optional[float] = None, station_id: Optional[str] = None,
                        sensor_id: Optional[str] = None, image_paths: Optional[List[str]] = None):
        with self.session_scope() as session:
            is_pass = True
            if min_limit is not None and value < min_limit:
                is_pass = False
            if max_limit is not None and value > max_limit:
                is_pass = False

            deviation = None
            if target_value is not None:
                deviation = value - target_value

            query = text("""
                INSERT INTO measurements (product_id, step_id, measurement_name, unit, value,
                                         min_limit, max_limit, target_value, is_pass, deviation,
                                         measured_at, station_id, sensor_id, image_paths)
                VALUES (:prod_id, :step_id, :name, :unit, :val, :min, :max, :target, :pass,
                        :deviation, NOW(), :station, :sensor, :images)
            """)
            session.execute(query, {
                'prod_id': product_id,
                'step_id': step_id,
                'name': measurement_name,
                'unit': unit,
                'val': value,
                'min': min_limit,
                'max': max_limit,
                'target': target_value,
                'pass': is_pass,
                'deviation': deviation,
                'station': station_id,
                'sensor': sensor_id,
                'images': image_paths or []
            })

    def get_product_history(self, serial_number: str) -> Dict[str, Any]:
        with self.session_scope() as session:
            product_query = text("""
                SELECT * FROM products WHERE serial_number = :serial
            """)
            product = session.execute(product_query, {'serial': serial_number}).fetchone()

            if not product:
                return None

            steps_query = text("""
                SELECT * FROM process_steps WHERE product_id = :id ORDER BY step_number
            """)
            steps = session.execute(steps_query, {'id': product.id}).fetchall()

            measurements_query = text("""
                SELECT * FROM measurements WHERE product_id = :id ORDER BY measured_at
            """)
            measurements = session.execute(measurements_query, {'id': product.id}).fetchall()

            return {
                'product': dict(product._mapping),
                'steps': [dict(step._mapping) for step in steps],
                'measurements': [dict(m._mapping) for m in measurements]
            }

    def get_batch_summary(self, batch_number: str) -> Dict[str, Any]:
        with self.session_scope() as session:
            summary_query = text("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN quality_result = 'ok' THEN 1 ELSE 0 END) as passed,
                    SUM(CASE WHEN quality_result = 'ng' THEN 1 ELSE 0 END) as failed,
                    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_time_seconds
                FROM products WHERE batch_number = :batch
            """)
            result = session.execute(summary_query, {'batch': batch_number}).fetchone()

            steps_query = text("""
                SELECT station_id, COUNT(*) as count, AVG(processing_duration_ms) as avg_duration
                FROM process_steps ps
                JOIN products p ON p.id = ps.product_id
                WHERE p.batch_number = :batch
                GROUP BY station_id
            """)
            station_stats = session.execute(steps_query, {'batch': batch_number}).fetchall()

            return {
                'batch_number': batch_number,
                'total_products': result.total,
                'passed': result.passed,
                'failed': result.failed,
                'yield_percent': (result.passed / result.total * 100) if result.total > 0 else 0,
                'avg_production_time_seconds': result.avg_time_seconds,
                'station_statistics': [dict(s._mapping) for s in station_stats]
            }


class ProductTracker:
    def __init__(self, config_path: str = "/config/tracker_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()

        db_url = self.config.get('postgres_url', 'postgresql://iot_user:iotpass2024@postgres:5432/product_history')
        self.db = ProductDatabase(db_url)

        mqtt_cfg = self.config.get('mqtt', {})
        self.mqtt_client = MQTTClient(
            broker=mqtt_cfg.get('broker', 'mosquitto'),
            port=mqtt_cfg.get('port', 1883)
        )

        self.running = False
        self.active_products: Dict[str, Dict] = {}

    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        return {
            'mqtt': {
                'broker': 'mosquitto',
                'port': 1883
            },
            'postgres_url': 'postgresql://iot_user:iotpass2024@postgres:5432/product_history',
            'stations': ['LOAD', 'FLOW1', 'FLOW2', 'QC1', 'CNC', 'QC2', 'PACK', 'OUT']
        }

    def handle_product_created(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            serial = payload.get('serial_number')
            batch = payload.get('batch_number')
            product_type = payload.get('product_type_id')
            variant = payload.get('variant_id')
            customer = payload.get('customer_id')
            wo = payload.get('work_order_id')

            product_id = self.db.create_product(serial, batch, product_type, variant, customer, wo, payload)

            self.active_products[serial] = {
                'product_id': product_id,
                'batch_number': batch,
                'current_step': 0,
                'step_entry_time': datetime.utcnow()
            }

            self.mqtt_client.publish('op10/product/status', {
                'serial_number': serial,
                'product_id': product_id,
                'status': 'created'
            })

            logger.info(f"Product tracked: {serial}")

        except Exception as e:
            logger.error(f"Product creation error: {e}")

    def handle_step_entry(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            serial = payload.get('serial_number')
            step_number = payload.get('step_number')
            step_name = payload.get('step_name')
            station_id = payload.get('station_id')
            position_id = payload.get('position_id')

            if serial in self.active_products:
                product = self.active_products[serial]
                product['current_step'] = step_number
                product['step_name'] = step_name
                product['station_id'] = station_id
                product['step_entry_time'] = datetime.utcnow()

                self.mqtt_client.publish('op10/product/status', {
                    'serial_number': serial,
                    'step_number': step_number,
                    'step_name': step_name,
                    'status': 'in_progress'
                })

                logger.info(f"Step entry: {serial} - {step_name}")

        except Exception as e:
            logger.error(f"Step entry error: {e}")

    def handle_step_exit(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            serial = payload.get('serial_number')
            step_number = payload.get('step_number')
            step_name = payload.get('step_name')
            station_id = payload.get('station_id')
            step_result = payload.get('result')
            cycle_count = payload.get('cycle_count')

            if serial in self.active_products:
                product = self.active_products[serial]
                entry_time = product.get('step_entry_time', datetime.utcnow())
                exit_time = datetime.utcnow()

                self.db.log_process_step(
                    product_id=product['product_id'],
                    step_number=step_number,
                    step_name=step_name,
                    station_id=station_id,
                    entry_time=entry_time,
                    exit_time=exit_time,
                    step_result=step_result,
                    cycle_count=cycle_count
                )

                self.mqtt_client.publish('op10/product/status', {
                    'serial_number': serial,
                    'step_number': step_number,
                    'step_name': step_name,
                    'status': 'completed',
                    'result': step_result
                })

        except Exception as e:
            logger.error(f"Step exit error: {e}")

    def handle_measurement(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            serial = payload.get('serial_number')
            step_id = payload.get('step_id')
            measurement_name = payload.get('measurement_name')
            value = payload.get('value')
            unit = payload.get('unit')
            min_limit = payload.get('min_limit')
            max_limit = payload.get('max_limit')
            target = payload.get('target_value')
            station_id = payload.get('station_id')
            sensor_id = payload.get('sensor_id')
            images = payload.get('images', [])

            if serial in self.active_products:
                product = self.active_products[serial]

                self.db.log_measurement(
                    product_id=product['product_id'],
                    step_id=step_id,
                    measurement_name=measurement_name,
                    value=value,
                    unit=unit,
                    min_limit=min_limit,
                    max_limit=max_limit,
                    target_value=target,
                    station_id=station_id,
                    sensor_id=sensor_id,
                    image_paths=images
                )

        except Exception as e:
            logger.error(f"Measurement error: {e}")

    def handle_product_completed(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload)
            serial = payload.get('serial_number')
            quality_result = payload.get('quality_result')

            if serial in self.active_products:
                product = self.active_products[serial]

                self.db.update_product_status(serial, 'completed', quality_result)

                del self.active_products[serial]

                self.mqtt_client.publish('op10/product/status', {
                    'serial_number': serial,
                    'status': 'completed',
                    'quality_result': quality_result
                })

                logger.info(f"Product completed: {serial} - {quality_result}")

        except Exception as e:
            logger.error(f"Product completion error: {e}")

    def setup_subscriptions(self):
        self.mqtt_client.subscribe('op10/product/created', self.handle_product_created)
        self.mqtt_client.subscribe('op10/product/step_entry', self.handle_step_entry)
        self.mqtt_client.subscribe('op10/product/step_exit', self.handle_step_exit)
        self.mqtt_client.subscribe('op10/product/measurement', self.handle_measurement)
        self.mqtt_client.subscribe('op10/product/completed', self.handle_product_completed)
        logger.info("MQTT subscriptions set up")

    def run(self):
        self.running = True
        self.setup_subscriptions()
        logger.info("Product tracking service started")

        try:
            while self.running:
                asyncio.run(asyncio.sleep(1))
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        self.mqtt_client.disconnect()
        logger.info("Product tracking service stopped")


def create_default_config():
    config = {
        'mqtt': {
            'broker': 'mosquitto',
            'port': 1883
        },
        'postgres_url': 'postgresql://iot_user:iotpass2024@postgres:5432/product_history',
        'stations': ['LOAD', 'FLOW1', 'FLOW2', 'QC1', 'CNC', 'QC2', 'PACK', 'OUT'],
        'batch_size': 100
    }

    config_path = Path("/config/tracker_config.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    logger.info(f"Default tracker config created at {config_path}")


def main():
    import os

    if os.environ.get("CREATE_TRACKER_CONFIG"):
        create_default_config()

    tracker = ProductTracker()
    tracker.run()


if __name__ == "__main__":
    main()

"""
Kafka Producer for publishing events to Kafka topics
"""
import json
import os
from typing import Dict, Any
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')


class EventProducer:
    """Kafka producer for publishing events"""
    
    def __init__(self):
        self.producer = None
        self._connect()
    
    def _connect(self):
        """Connect to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"✅ Kafka producer connected to {KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kafka: {e}")
            raise
    
    def publish_event(self, topic: str, event: Dict[str, Any], key: str = None):
        """
        Publish an event to a Kafka topic
        
        Args:
            topic: Kafka topic name
            event: Event data (dict)
            key: Optional message key for partitioning
        """
        try:
            future = self.producer.send(topic, value=event, key=key)
            record_metadata = future.get(timeout=10)
            logger.info(
                f"📤 Event published to {topic} "
                f"[partition={record_metadata.partition}, offset={record_metadata.offset}]"
            )
            return True
        except KafkaError as e:
            logger.error(f"❌ Failed to publish to {topic}: {e}")
            return False
    
    def close(self):
        """Close the producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed")


# Singleton instance
_producer_instance = None


def get_producer():
    """Get or create producer singleton"""
    global _producer_instance
    if _producer_instance is None:
        _producer_instance = EventProducer()
    return _producer_instance

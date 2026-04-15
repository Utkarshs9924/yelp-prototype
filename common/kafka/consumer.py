"""
Kafka Consumer for consuming events from Kafka topics
"""
import json
import os
from typing import Callable, List
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')


class EventConsumer:
    """Kafka consumer for consuming events"""
    
    def __init__(self, topics: List[str], group_id: str, handler: Callable):
        """
        Initialize consumer
        
        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group ID
            handler: Function to handle each message
        """
        self.topics = topics
        self.group_id = group_id
        self.handler = handler
        self.consumer = None
        self._connect()
    
    def _connect(self):
        """Connect to Kafka"""
        try:
            self.consumer = KafkaConsumer(
                *self.topics,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                group_id=self.group_id,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                auto_offset_reset='earliest',  # Start from beginning if no offset
                enable_auto_commit=True,
                auto_commit_interval_ms=1000
            )
            logger.info(
                f"✅ Kafka consumer connected [{self.group_id}] "
                f"subscribed to {self.topics}"
            )
        except Exception as e:
            logger.error(f"❌ Failed to connect consumer: {e}")
            raise
    
    def start_consuming(self):
        """Start consuming messages"""
        logger.info(f"🎧 Starting to consume messages from {self.topics}...")
        try:
            for message in self.consumer:
                try:
                    logger.info(
                        f"📥 Received from {message.topic} "
                        f"[partition={message.partition}, offset={message.offset}]"
                    )
                    # Call the handler
                    self.handler(message.topic, message.value, message.key)
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    # Continue processing other messages
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            self.close()
    
    def close(self):
        """Close the consumer"""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")

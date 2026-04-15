# Kafka module exports
from .producer import EventProducer, get_producer
from .consumer import EventConsumer

__all__ = ['EventProducer', 'get_producer', 'EventConsumer']

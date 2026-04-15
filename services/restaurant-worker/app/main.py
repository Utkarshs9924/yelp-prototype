"""
Restaurant Worker Service - Consumer
Consumes restaurant events from Kafka and processes them
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.kafka import EventConsumer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_restaurant_event(topic: str, event: dict, key: str):
    """Handle restaurant events from Kafka"""
    logger.info(f"📨 Processing event from {topic}: {event}")
    
    try:
        if topic == "restaurant.created":
            handle_restaurant_created(event)
        elif topic == "restaurant.updated":
            handle_restaurant_updated(event)
        elif topic == "restaurant.claimed":
            handle_restaurant_claimed(event)
        else:
            logger.warning(f"⚠️  Unknown topic: {topic}")
            
    except Exception as e:
        logger.error(f"❌ Error handling event: {e}")


def handle_restaurant_created(event: dict):
    """Process restaurant creation"""
    logger.info(f"✅ Restaurant created: {event['name']} [ID: {event['restaurant_id']}]")
    # Could update search index, send notifications, etc.


def handle_restaurant_updated(event: dict):
    """Process restaurant update"""
    logger.info(f"✅ Restaurant updated: {event['restaurant_id']}")
    # Could update caches, search index, etc.


def handle_restaurant_claimed(event: dict):
    """Process restaurant claim by owner"""
    logger.info(f"✅ Restaurant claimed: {event.get('restaurant_id')}")
    # Could send verification email, update ownership records, etc.


def main():
    """Start the consumer"""
    logger.info("🚀 Starting Restaurant Worker Service...")
    
    topics = ["restaurant.created", "restaurant.updated", "restaurant.claimed"]
    
    consumer = EventConsumer(
        topics=topics,
        group_id="restaurant-worker-group",
        handler=handle_restaurant_event
    )
    
    consumer.start_consuming()


if __name__ == "__main__":
    main()

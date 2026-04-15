"""
User Worker Service - Consumer
Consumes user events from Kafka and processes them
"""
import sys
import os

# Add parent directory to path to import common module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.kafka import EventConsumer
from common.database import get_users_collection
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_user_event(topic: str, event: dict, key: str):
    """
    Handle user events from Kafka
    
    Args:
        topic: Kafka topic name
        event: Event data
        key: Message key (user_id)
    """
    logger.info(f"📨 Processing event from {topic}: {event}")
    
    try:
        if topic == "user.created":
            handle_user_created(event)
        elif topic == "user.updated":
            handle_user_updated(event)
        elif topic == "user.login":
            handle_user_login(event)
        else:
            logger.warning(f"⚠️  Unknown topic: {topic}")
            
    except Exception as e:
        logger.error(f"❌ Error handling event: {e}")


def handle_user_created(event: dict):
    """Log user creation event (already saved in API)"""
    logger.info(f"✅ User created: {event['email']} [ID: {event['user_id']}]")
    # Could send welcome email, create analytics record, etc.


def handle_user_updated(event: dict):
    """Log user update event"""
    logger.info(f"✅ User updated: {event['user_id']}")
    # Could update search index, sync with external systems, etc.


def handle_user_login(event: dict):
    """Track user login"""
    logger.info(f"✅ User login: {event['email']} at {event['timestamp']}")
    # Could update last_login, track analytics, detect anomalies, etc.


def main():
    """Start the consumer"""
    logger.info("🚀 Starting User Worker Service...")
    
    # Topics to subscribe to
    topics = ["user.created", "user.updated", "user.login"]
    
    # Create consumer
    consumer = EventConsumer(
        topics=topics,
        group_id="user-worker-group",
        handler=handle_user_event
    )
    
    # Start consuming
    consumer.start_consuming()


if __name__ == "__main__":
    main()

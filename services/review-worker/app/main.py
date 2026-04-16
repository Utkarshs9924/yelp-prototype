"""
Review Worker Service - Consumer
Consumes review events from Kafka and processes them
Updates restaurant ratings and statistics
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from common.kafka import EventConsumer
from common.database import get_reviews_collection, get_restaurants_collection
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_review_event(topic: str, event: dict, key: str):
    """Handle review events from Kafka"""
    logger.info(f"📨 Processing event from {topic}: {event}")
    
    try:
        if topic == "review.created":
            handle_review_created(event)
        elif topic == "review.updated":
            handle_review_updated(event)
        elif topic == "review.deleted":
            handle_review_deleted(event)
        else:
            logger.warning(f"⚠️  Unknown topic: {topic}")
            
    except Exception as e:
        logger.error(f"❌ Error handling event: {e}")


def update_restaurant_rating(restaurant_id: str):
    """Recalculate and update restaurant rating"""
    try:
        reviews = get_reviews_collection()
        restaurants = get_restaurants_collection()
        
        # Calculate average rating and count
        pipeline = [
            {"$match": {"restaurant_id": restaurant_id}},
            {"$group": {
                "_id": "$restaurant_id",
                "average_rating": {"$avg": "$rating"},
                "review_count": {"$sum": 1}
            }}
        ]
        
        result = list(reviews.aggregate(pipeline))
        
        if result:
            avg_rating = result[0]["average_rating"]
            count = result[0]["review_count"]
        else:
            avg_rating = 0.0
            count = 0
        
        # Update restaurant
        restaurants.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$set": {
                "average_rating": round(avg_rating, 2),
                "review_count": count
            }}
        )
        
        logger.info(f"✅ Updated restaurant {restaurant_id}: avg={avg_rating:.2f}, count={count}")
        
    except Exception as e:
        logger.error(f"❌ Error updating restaurant rating: {e}")


def handle_review_created(event: dict):
    """Process review creation"""
    logger.info(f"✅ Review created: {event['review_id']} with rating {event['rating']}")
    update_restaurant_rating(event["restaurant_id"])


def handle_review_updated(event: dict):
    """Process review update"""
    logger.info(f"✅ Review updated: {event['review_id']}")
    update_restaurant_rating(event["restaurant_id"])


def handle_review_deleted(event: dict):
    """Process review deletion"""
    logger.info(f"✅ Review deleted: {event['review_id']}")
    update_restaurant_rating(event["restaurant_id"])


def main():
    """Start the consumer"""
    logger.info("🚀 Starting Review Worker Service...")
    
    topics = ["review.created", "review.updated", "review.deleted"]
    
    consumer = EventConsumer(
        topics=topics,
        group_id="review-worker-group",
        handler=handle_review_event
    )
    
    consumer.start_consuming()


if __name__ == "__main__":
    main()

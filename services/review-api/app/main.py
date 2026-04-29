"""
Review API Service - Producer
Handles review CRUD operations
Publishes events to Kafka for async processing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from common.kafka import get_producer
from common.database import get_reviews_collection, get_restaurants_collection
from bson import ObjectId
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Review API Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReviewCreate(BaseModel):
    restaurant_id: str
    user_id: str
    rating: int
    comment: Optional[str] = ""


def serialize_doc(doc):
    """Recursively serialize MongoDB doc - handles ObjectId and datetime"""
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_doc(i) for i in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    return doc


def restaurant_id_query(restaurant_id: str) -> dict:
    """
    Build a query that matches restaurant_id stored as either
    a plain string (new reviews) or ObjectId (migrated reviews).
    """
    if ObjectId.is_valid(restaurant_id):
        return {"$or": [
            {"restaurant_id": restaurant_id},
            {"restaurant_id": ObjectId(restaurant_id)}
        ]}
    return {"restaurant_id": restaurant_id}


@app.get("/")
def root():
    return {"service": "Review API", "status": "running"}


@app.post("/reviews")
def create_review(review: ReviewCreate):
    """Create review - store as string IDs, publish event to Kafka"""
    try:
        reviews = get_reviews_collection()

        if not (1 <= review.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        review_doc = {
            "restaurant_id": review.restaurant_id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = reviews.insert_one(review_doc)
        review_id = str(result.inserted_id)

        try:
            producer = get_producer()
            producer.publish_event(
                topic="review.created",
                event={
                    "review_id": review_id,
                    "restaurant_id": review.restaurant_id,
                    "user_id": review.user_id,
                    "rating": review.rating,
                    "timestamp": datetime.utcnow().isoformat()
                },
                key=review_id
            )
        except Exception as kafka_err:
            logger.warning(f"⚠️ Kafka unavailable, skipping event: {kafka_err}")

        logger.info(f"✅ Review created: {review_id} for restaurant {review.restaurant_id}")
        return {"message": "Review created successfully", "id": review_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Create review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(restaurant_id: str):
    """
    Get all reviews for a restaurant.
    Queries by both string and ObjectId to handle migrated + new reviews.
    """
    try:
        reviews = get_reviews_collection()
        query = restaurant_id_query(restaurant_id)
        review_list = list(reviews.find(query).sort("created_at", -1))

        for r in review_list:
            r["id"] = str(r.pop("_id"))

        return {"reviews": [serialize_doc(r) for r in review_list]}

    except Exception as e:
        logger.error(f"❌ Get reviews error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/reviews/{review_id}")
def update_review(review_id: str, update: ReviewCreate):
    """Update review - publish event to Kafka"""
    try:
        reviews = get_reviews_collection()

        if not (1 <= update.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        result = reviews.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": {
                "rating": update.rating,
                "comment": update.comment,
                "updated_at": datetime.utcnow()
            }}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")

        try:
            producer = get_producer()
            producer.publish_event(
                topic="review.updated",
                event={
                    "review_id": review_id,
                    "restaurant_id": update.restaurant_id,
                    "rating": update.rating,
                    "timestamp": datetime.utcnow().isoformat()
                },
                key=review_id
            )
        except Exception as kafka_err:
            logger.warning(f"⚠️ Kafka unavailable, skipping event: {kafka_err}")

        logger.info(f"✅ Review updated: {review_id}")
        return {"message": "Review updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/reviews/{review_id}")
def delete_review(review_id: str, restaurant_id: str):
    """Delete review - publish event to Kafka"""
    try:
        reviews = get_reviews_collection()

        result = reviews.delete_one({"_id": ObjectId(review_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Review not found")

        try:
            producer = get_producer()
            producer.publish_event(
                topic="review.deleted",
                event={
                    "review_id": review_id,
                    "restaurant_id": restaurant_id,
                    "timestamp": datetime.utcnow().isoformat()
                },
                key=review_id
            )
        except Exception as kafka_err:
            logger.warning(f"⚠️ Kafka unavailable, skipping event: {kafka_err}")

        logger.info(f"✅ Review deleted: {review_id}")
        return {"message": "Review deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Delete review error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
"""
Review API Service - Producer
Handles review CRUD operations
Publishes events to Kafka for async processing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from common.kafka import get_producer
from common.database import get_reviews_collection, get_restaurants_collection, get_users_collection
from common.utils.s3_storage import upload_to_s3
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
    photo_url: Optional[str] = None


def serialize_doc(doc):
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
    if ObjectId.is_valid(restaurant_id):
        return {"$or": [
            {"restaurant_id": restaurant_id},
            {"restaurant_id": ObjectId(restaurant_id)}
        ]}
    return {"restaurant_id": restaurant_id}


def get_user_name(user_id: str) -> str:
    try:
        users = get_users_collection()
        user = None
        if ObjectId.is_valid(user_id):
            user = users.find_one({"_id": ObjectId(user_id)})
        if not user:
            user = users.find_one({"_id": user_id})
        if user:
            return user.get("name", "Anonymous")
    except Exception:
        pass
    return "Anonymous"


@app.get("/")
def root():
    return {"service": "Review API", "status": "running"}


@app.post("/reviews/upload-photo")
async def upload_review_photo(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    """Upload a photo for a review to S3"""
    try:
        contents = await file.read()
        photo_url = await upload_to_s3(
            contents, file.filename, file.content_type, folder="review-photos"
        )
        logger.info(f"✅ Review photo uploaded: {photo_url}")
        return {"photo_url": photo_url}
    except Exception as e:
        logger.error(f"❌ Review photo upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reviews")
def create_review(review: ReviewCreate):
    try:
        reviews = get_reviews_collection()

        if not (1 <= review.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

        review_doc = {
            "restaurant_id": review.restaurant_id,
            "user_id": review.user_id,
            "rating": review.rating,
            "comment": review.comment,
            "photo_url": review.photo_url,
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
    try:
        reviews = get_reviews_collection()
        query = restaurant_id_query(restaurant_id)
        review_list = list(reviews.find(query).sort("created_at", -1))

        user_id_set = set()
        for r in review_list:
            uid = r.get("user_id")
            if uid:
                user_id_set.add(str(uid) if isinstance(uid, ObjectId) else uid)

        user_name_cache = {}
        for uid in user_id_set:
            user_name_cache[uid] = get_user_name(uid)

        for r in review_list:
            r["id"] = str(r.pop("_id"))
            uid = r.get("user_id")
            uid_str = str(uid) if isinstance(uid, ObjectId) else uid
            r["user_id"] = uid_str
            r["user_name"] = user_name_cache.get(uid_str, "Anonymous")

        return {"reviews": [serialize_doc(r) for r in review_list]}

    except Exception as e:
        logger.error(f"❌ Get reviews error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/reviews/{review_id}")
def update_review(review_id: str, update: ReviewCreate):
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
def delete_review(review_id: str, restaurant_id: Optional[str] = None):
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
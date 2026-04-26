"""
Owner API Service - Producer
Handles restaurant owner dashboard and management
Publishes events to Kafka for async processing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from common.kafka import get_producer
from common.database import get_restaurants_collection, get_reviews_collection
from bson import ObjectId
from datetime import datetime
import jwt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Owner API Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET = os.getenv("JWT_SECRET", "akash_yelp_lab_secret_key_2024_!@#")
JWT_ALGORITHM = "HS256"


def get_owner_id(authorization: str = Header(None)) -> str:
    """Extract owner_id from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


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


class RestaurantSubmit(BaseModel):
    name: str
    cuisine_type: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    hours_of_operation: Optional[str] = None
    pricing_tier: Optional[str] = "$"
    amenities: Optional[str] = None
    ambiance: Optional[str] = None


@app.get("/")
def root():
    return {"service": "Owner API", "status": "running"}


@app.get("/owner/restaurants")
def get_owner_restaurants(authorization: str = Header(None)):
    """Get all restaurants owned by the current owner"""
    owner_id = get_owner_id(authorization)
    try:
        restaurants = get_restaurants_collection()
        results = list(restaurants.find({"owner_id": owner_id}))
        for r in results:
            r["id"] = str(r.pop("_id"))
        return {"restaurants": [serialize_doc(r) for r in results]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get owner restaurants error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/owner/dashboard")
def get_owner_dashboard(authorization: str = Header(None)):
    """Get owner dashboard stats"""
    owner_id = get_owner_id(authorization)
    try:
        restaurants = get_restaurants_collection()
        reviews = get_reviews_collection()

        owner_restaurants = list(restaurants.find({"owner_id": owner_id}))
        restaurant_ids = [str(r["_id"]) for r in owner_restaurants]

        total_reviews = reviews.count_documents({"restaurant_id": {"$in": restaurant_ids}})

        ratings = [r.get("average_rating", 0) for r in owner_restaurants if r.get("average_rating")]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

        logger.info(f"✅ Dashboard loaded for owner {owner_id}")

        return {
            "total_restaurants": len(owner_restaurants),
            "total_reviews": total_reviews,
            "average_rating": avg_rating,
            "restaurants": [serialize_doc({**r, "id": str(r["_id"])}) for r in owner_restaurants]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/owner/restaurants")
def submit_restaurant(restaurant: RestaurantSubmit, authorization: str = Header(None)):
    """Submit a new restaurant (pending approval) - publish event to Kafka"""
    owner_id = get_owner_id(authorization)
    try:
        restaurants = get_restaurants_collection()

        restaurant_doc = {
            **restaurant.dict(),
            "owner_id": owner_id,
            "status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "views": 0,
            "average_rating": 0.0,
            "review_count": 0
        }

        result = restaurants.insert_one(restaurant_doc)
        restaurant_id = str(result.inserted_id)

        producer = get_producer()
        producer.publish_event(
            topic="restaurant.created",
            event={
                "restaurant_id": restaurant_id,
                "name": restaurant.name,
                "owner_id": owner_id,
                "status": "pending",
                "timestamp": datetime.utcnow().isoformat()
            },
            key=restaurant_id
        )

        logger.info(f"✅ Restaurant submitted by owner {owner_id}: {restaurant_id}")

        return {"message": "Restaurant submitted for approval", "id": restaurant_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Submit restaurant error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/owner/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(restaurant_id: str, authorization: str = Header(None)):
    """Get reviews for an owned restaurant"""
    owner_id = get_owner_id(authorization)
    try:
        restaurants = get_restaurants_collection()
        restaurant = restaurants.find_one({"_id": ObjectId(restaurant_id), "owner_id": owner_id})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found or not owned by you")

        reviews = get_reviews_collection()
        review_list = list(reviews.find({"restaurant_id": restaurant_id}).sort("created_at", -1))
        for r in review_list:
            r["id"] = str(r.pop("_id"))

        return {"reviews": [serialize_doc(r) for r in review_list]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Get reviews error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

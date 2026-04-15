"""
Restaurant API Service - Producer
Handles restaurant CRUD operations
Publishes events to Kafka for async processing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from common.kafka import get_producer
from common.database import get_restaurants_collection, get_reviews_collection
from bson import ObjectId
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Restaurant API Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RestaurantCreate(BaseModel):
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
    return {"service": "Restaurant API", "status": "running"}


@app.post("/restaurants")
def create_restaurant(restaurant: RestaurantCreate):
    """Create restaurant - publish event to Kafka"""
    try:
        restaurants = get_restaurants_collection()
        
        restaurant_doc = {
            **restaurant.dict(),
            "status": "approved",
            "owner_id": None,
            "created_by_user_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "views": 0,
            "average_rating": 0.0,
            "review_count": 0
        }
        
        result = restaurants.insert_one(restaurant_doc)
        restaurant_id = str(result.inserted_id)
        
        # Publish event to Kafka
        producer = get_producer()
        producer.publish_event(
            topic="restaurant.created",
            event={
                "restaurant_id": restaurant_id,
                "name": restaurant.name,
                "city": restaurant.city,
                "cuisine_type": restaurant.cuisine_type,
                "timestamp": datetime.utcnow().isoformat()
            },
            key=restaurant_id
        )
        
        logger.info(f"✅ Restaurant created: {restaurant.name}")
        
        return {"message": "Restaurant created successfully", "id": restaurant_id}
        
    except Exception as e:
        logger.error(f"❌ Create restaurant error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurants")
def get_restaurants(page: int = 1, limit: int = 30):
    """Get all restaurants with pagination"""
    try:
        restaurants = get_restaurants_collection()
        
        skip = (page - 1) * limit
        
        restaurant_list = list(restaurants.find().skip(skip).limit(limit))
        total = restaurants.count_documents({})
        
        # Convert ObjectId to string
        for r in restaurant_list:
            r["id"] = str(r.pop("_id"))
        
        return {
            "restaurants": restaurant_list,
            "total": total,
            "page": page,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"❌ Get restaurants error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: str):
    """Get restaurant by ID"""
    try:
        restaurants = get_restaurants_collection()
        restaurant = restaurants.find_one({"_id": ObjectId(restaurant_id)})
        
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        restaurant["id"] = str(restaurant.pop("_id"))
        
        return restaurant
        
    except Exception as e:
        logger.error(f"❌ Get restaurant error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/restaurants/{restaurant_id}")
def update_restaurant(restaurant_id: str, update: RestaurantCreate):
    """Update restaurant - publish event to Kafka"""
    try:
        restaurants = get_restaurants_collection()
        
        result = restaurants.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$set": {
                **update.dict(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Publish event to Kafka
        producer = get_producer()
        producer.publish_event(
            topic="restaurant.updated",
            event={
                "restaurant_id": restaurant_id,
                "name": update.name,
                "timestamp": datetime.utcnow().isoformat()
            },
            key=restaurant_id
        )
        
        logger.info(f"✅ Restaurant updated: {restaurant_id}")
        
        return {"message": "Restaurant updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update restaurant error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurants/search")
def search_restaurants(q: Optional[str] = None, cuisine: Optional[str] = None, city: Optional[str] = None):
    """Search restaurants"""
    try:
        restaurants = get_restaurants_collection()
        
        query = {}
        if q:
            query["$or"] = [
                {"name": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}}
            ]
        if cuisine:
            query["cuisine_type"] = {"$regex": cuisine, "$options": "i"}
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        
        results = list(restaurants.find(query).limit(50))
        
        for r in results:
            r["id"] = str(r.pop("_id"))
        
        return {"restaurants": results}
        
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

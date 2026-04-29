"""
Restaurant API Service - Producer
Handles restaurants, favorites, preferences, history, photos, menus
This is the catch-all service routed by nginx for everything not
handled by user-api, review-api, owner-api, or backend.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from common.kafka import get_producer
from common.database import (
    get_restaurants_collection, get_reviews_collection,
    get_favorites_collection, get_preferences_collection,
    get_photos_collection
)
from common.utils.s3_storage import upload_to_s3, delete_from_s3
from bson import ObjectId
from datetime import datetime
import jwt
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

JWT_SECRET = os.getenv("JWT_SECRET", "akash_yelp_lab_secret_key_2024_!@#")
JWT_ALGORITHM = "HS256"


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def get_user_id(authorization: str = None) -> str:
    """Extract user_id from JWT Bearer token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def dual_id_query(field: str, value: str) -> dict:
    """
    Build a MongoDB query that matches a field stored as either
    a plain string or an ObjectId — handles migrated vs new documents.
    """
    if ObjectId.is_valid(value):
        return {"$or": [{field: value}, {field: ObjectId(value)}]}
    return {field: value}


# ── Models ────────────────────────────────────────────────────────────────────

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


class PreferencesUpdate(BaseModel):
    cuisine_preferences: Optional[str] = None
    price_range: Optional[str] = None
    dietary_needs: Optional[str] = None
    ambiance_preference: Optional[str] = None
    sort_preference: Optional[str] = None


# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"service": "Restaurant API", "status": "running"}


# ── Restaurants ───────────────────────────────────────────────────────────────

@app.get("/restaurants")
def get_restaurants(page: int = 1, limit: int = 30):
    try:
        restaurants = get_restaurants_collection()
        skip = (page - 1) * limit
        restaurant_list = list(restaurants.find().skip(skip).limit(limit))
        total = restaurants.count_documents({})
        result = []
        for r in restaurant_list:
            r["id"] = str(r.pop("_id"))
            result.append(serialize_doc(r))
        return {"restaurants": result, "total": total, "page": page, "limit": limit}
    except Exception as e:
        logger.error(f"❌ Get restaurants error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurants/search")
def search_restaurants(
    q: Optional[str] = None,
    name: Optional[str] = None,
    cuisine: Optional[str] = None,
    city: Optional[str] = None,
    pricing_tier: Optional[str] = None,
    amenities: Optional[str] = None,
    page: int = 1,
    limit: int = 30
):
    try:
        restaurants = get_restaurants_collection()
        query = {}
        search_term = q or name
        if search_term:
            query["$or"] = [
                {"name": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ]
        if cuisine:
            query["cuisine_type"] = {"$regex": cuisine, "$options": "i"}
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        if pricing_tier:
            query["pricing_tier"] = pricing_tier
        if amenities:
            amenity_list = [a.strip() for a in amenities.split(',') if a.strip()]
            for a in amenity_list:
                query["amenities"] = {"$regex": a, "$options": "i"}
        skip = (page - 1) * limit
        total = restaurants.count_documents(query)
        results = list(restaurants.find(query).skip(skip).limit(limit))
        result = []
        for r in results:
            r["id"] = str(r.pop("_id"))
            result.append(serialize_doc(r))
        return {"restaurants": result, "total": total, "page": page, "limit": limit}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurants/{restaurant_id}/menu")
def get_restaurant_menu(restaurant_id: str):
    """Return embedded menu_items from the restaurant document"""
    try:
        restaurants = get_restaurants_collection()
        restaurant = restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        menu_items = restaurant.get("menu_items", [])
        return {"menu_items": serialize_doc(menu_items)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restaurants/{restaurant_id}/claim")
def claim_restaurant(restaurant_id: str, authorization: str = Header(None)):
    """Owner claims an unclaimed restaurant"""
    user_id = get_user_id(authorization)
    try:
        restaurants = get_restaurants_collection()
        restaurant = restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        if restaurant.get("owner_id"):
            raise HTTPException(status_code=409, detail="Restaurant already claimed")

        restaurants.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$set": {"owner_id": user_id, "updated_at": datetime.utcnow()}}
        )

        try:
            producer = get_producer()
            producer.publish_event(
                topic="restaurant.claimed",
                event={"restaurant_id": restaurant_id, "owner_id": user_id,
                       "timestamp": datetime.utcnow().isoformat()},
                key=restaurant_id
            )
        except Exception as kafka_err:
            logger.warning(f"⚠️ Kafka unavailable, skipping event: {kafka_err}")

        return {"message": "Restaurant claimed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: str):
    try:
        restaurants = get_restaurants_collection()
        restaurant = restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        restaurant["id"] = str(restaurant.pop("_id"))
        return serialize_doc(restaurant)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/restaurants")
def create_restaurant(restaurant: RestaurantCreate):
    try:
        restaurants = get_restaurants_collection()
        restaurant_doc = {
            **restaurant.dict(),
            "status": "approved",
            "owner_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "views": 0,
            "average_rating": 0.0,
            "review_count": 0,
            "menu_items": []
        }
        result = restaurants.insert_one(restaurant_doc)
        restaurant_id = str(result.inserted_id)
        try:
            producer = get_producer()
            producer.publish_event(
                topic="restaurant.created",
                event={"restaurant_id": restaurant_id, "name": restaurant.name},
                key=restaurant_id
            )
        except Exception as kafka_err:
            logger.warning(f"⚠️ Kafka unavailable, skipping event: {kafka_err}")
        return {"message": "Restaurant created successfully", "id": restaurant_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/restaurants/{restaurant_id}")
def update_restaurant(restaurant_id: str, update: RestaurantCreate):
    try:
        restaurants = get_restaurants_collection()
        result = restaurants.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$set": {**update.dict(), "updated_at": datetime.utcnow()}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        try:
            producer = get_producer()
            producer.publish_event(
                topic="restaurant.updated",
                event={"restaurant_id": restaurant_id},
                key=restaurant_id
            )
        except Exception as kafka_err:
            logger.warning(f"⚠️ Kafka unavailable, skipping event: {kafka_err}")
        return {"message": "Restaurant updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Photos ────────────────────────────────────────────────────────────────────

@app.post("/restaurants/{restaurant_id}/photos")
async def upload_photo(restaurant_id: str, file: UploadFile = File(...),
                       authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    try:
        contents = await file.read()
        photo_url = await upload_to_s3(
            contents, file.filename, file.content_type, folder="restaurant-photos"
        )
        photos = get_photos_collection()
        result = photos.insert_one({
            "restaurant_id": restaurant_id,
            "user_id": user_id,
            "photo_url": photo_url,
            "caption": "",
            "created_at": datetime.utcnow()
        })
        return {"message": "Photo uploaded", "photo_id": str(result.inserted_id), "photo_url": photo_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/photos/{photo_id}")
async def delete_photo(photo_id: str, authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    try:
        photos = get_photos_collection()
        photo = photos.find_one({"_id": ObjectId(photo_id)})
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found")
        if str(photo.get("user_id")) != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        await delete_from_s3(photo["photo_url"])
        photos.delete_one({"_id": ObjectId(photo_id)})
        return {"message": "Photo deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Favorites ─────────────────────────────────────────────────────────────────

@app.get("/favorites")
def get_favorites(authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    try:
        favorites = get_favorites_collection()
        restaurants = get_restaurants_collection()

        user_query = dual_id_query("user_id", user_id)
        favs = list(favorites.find(user_query))

        result = []
        for fav in favs:
            rid = str(fav["restaurant_id"]) if isinstance(fav["restaurant_id"], ObjectId) else fav["restaurant_id"]
            try:
                restaurant = restaurants.find_one({"_id": ObjectId(rid)})
                if restaurant:
                    restaurant["id"] = str(restaurant.pop("_id"))
                    result.append(serialize_doc(restaurant))
            except Exception:
                continue

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/favorites")
def add_favorite(data: dict, authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    restaurant_id = data.get("restaurant_id")
    if not restaurant_id:
        raise HTTPException(status_code=400, detail="restaurant_id is required")
    try:
        favorites = get_favorites_collection()

        # Check for existing using both string and ObjectId
        existing_query = {
            "$and": [
                dual_id_query("user_id", user_id),
                dual_id_query("restaurant_id", restaurant_id)
            ]
        }
        if favorites.find_one(existing_query):
            raise HTTPException(status_code=409, detail="Already in favourites")

        favorites.insert_one({
            "user_id": user_id,
            "restaurant_id": restaurant_id,
            "created_at": datetime.utcnow()
        })
        return {"message": "Restaurant added to favourites"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/favorites/check/{restaurant_id}")
def check_favorite(restaurant_id: str, authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    try:
        favorites = get_favorites_collection()
        query = {
            "$and": [
                dual_id_query("user_id", user_id),
                dual_id_query("restaurant_id", restaurant_id)
            ]
        }
        exists = favorites.find_one(query) is not None
        return {"is_favourite": exists}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/favorites/{restaurant_id}")
def remove_favorite(restaurant_id: str, authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    try:
        favorites = get_favorites_collection()
        query = {
            "$and": [
                dual_id_query("user_id", user_id),
                dual_id_query("restaurant_id", restaurant_id)
            ]
        }
        result = favorites.delete_one(query)
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Favourite not found")
        return {"message": "Favourite removed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Preferences ───────────────────────────────────────────────────────────────

@app.get("/preferences")
def get_preferences(authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    try:
        preferences = get_preferences_collection()
        pref = preferences.find_one(dual_id_query("user_id", user_id))
        if not pref:
            return {}
        pref["id"] = str(pref.pop("_id"))
        return serialize_doc(pref)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/preferences")
def update_preferences(update: PreferencesUpdate, authorization: str = Header(None)):
    user_id = get_user_id(authorization)
    try:
        preferences = get_preferences_collection()
        preferences.update_one(
            {"user_id": user_id},
            {"$set": {
                **update.dict(exclude_none=True),
                "user_id": user_id,
                "updated_at": datetime.utcnow()
            }},
            upsert=True  # creates the doc if it doesn't exist yet
        )
        return {"message": "Preferences updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── History ───────────────────────────────────────────────────────────────────

@app.get("/history")
def get_history(authorization: str = Header(None)):
    """Return user's review history + restaurants they added"""
    user_id = get_user_id(authorization)
    try:
        reviews = get_reviews_collection()
        restaurants = get_restaurants_collection()

        # Get reviews by this user (match both string and ObjectId)
        review_query = dual_id_query("user_id", user_id)
        user_reviews = list(reviews.find(review_query).sort("created_at", -1).limit(50))

        history_items = []

        for r in user_reviews:
            rid = str(r["restaurant_id"]) if isinstance(r["restaurant_id"], ObjectId) else r["restaurant_id"]
            try:
                restaurant = restaurants.find_one({"_id": ObjectId(rid)})
                restaurant_name = restaurant["name"] if restaurant else "Unknown Restaurant"
            except Exception:
                restaurant_name = "Unknown Restaurant"

            history_items.append({
                "type": "review",
                "review_id": str(r["_id"]),
                "restaurant_id": rid,
                "restaurant_name": restaurant_name,
                "rating": r.get("rating"),
                "comment": r.get("comment"),
                "created_at": r["created_at"].isoformat() if isinstance(r.get("created_at"), datetime) else str(r.get("created_at"))
            })

        return {"history": history_items}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
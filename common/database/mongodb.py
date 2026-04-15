"""
MongoDB database connection and helper functions
"""
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from typing import Optional
import os

# MongoDB connection string
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://akashkumarsenthilkumar_db_user:mTnLH54vQAmmNjir@yelp.wvxiqvo.mongodb.net/?retryWrites=true&w=majority&appName=yelp"
)
DB_NAME = os.getenv("DB_NAME", "yelp_db")

_client: Optional[MongoClient] = None
_db = None


def get_mongo_client():
    """Get MongoDB client instance (singleton)"""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    return _client


def get_database():
    """Get MongoDB database instance"""
    global _db
    if _db is None:
        client = get_mongo_client()
        _db = client[DB_NAME]
    return _db


def close_mongo_connection():
    """Close MongoDB connection"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None


# Collection getters
def get_users_collection():
    """Get users collection"""
    db = get_database()
    return db['users']


def get_restaurants_collection():
    """Get restaurants collection"""
    db = get_database()
    return db['restaurants']


def get_reviews_collection():
    """Get reviews collection"""
    db = get_database()
    return db['reviews']


def get_favorites_collection():
    """Get favorites collection"""
    db = get_database()
    return db['favorites']


def get_sessions_collection():
    """Get sessions collection"""
    db = get_database()
    return db['sessions']


def get_preferences_collection():
    """Get user preferences collection"""
    db = get_database()
    return db['preferences']


def get_photos_collection():
    """Get photos collection"""
    db = get_database()
    return db['photos']


def get_menus_collection():
    """Get menus collection"""
    db = get_database()
    return db['menus']

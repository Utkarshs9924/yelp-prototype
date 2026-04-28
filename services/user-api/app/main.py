"""
User API Service - Producer
Handles user authentication and profile management
Publishes events to Kafka for async processing
"""
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path to import common module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import bcrypt
import jwt
from datetime import datetime, timedelta
from common.kafka import get_producer
from common.database import get_users_collection, get_sessions_collection
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="User API Service")

# Thread pool for CPU-bound bcrypt operations
_executor = ThreadPoolExecutor(max_workers=10)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "akash_yelp_lab_secret_key_2024_!@#")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


# Pydantic Models
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "user"


class LoginRequest(BaseModel):
    email: str
    password: str


class UserProfileUpdate(BaseModel):
    name: str
    phone: Optional[str] = ""
    about_me: Optional[str] = ""
    city: Optional[str] = ""
    country: Optional[str] = ""
    languages: Optional[str] = ""
    gender: Optional[str] = ""


# Helper Functions
def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Routes
@app.get("/")
def root():
    return {"service": "User API", "status": "running"}


@app.post("/signup")
def signup(user: SignupRequest):
    """User signup - publish event to Kafka"""
    try:
        users = get_users_collection()
        
        # Check if email exists
        existing_user = users.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        hashed_password = bcrypt.hashpw(
            user.password.encode('utf-8'),
            bcrypt.gensalt(rounds=4)
        ).decode('utf-8')
        
        # Prepare user data
        role = user.role if user.role in ["user", "owner"] else "user"
        is_approved = True if role == "user" else False
        
        user_doc = {
            "name": user.name,
            "email": user.email,
            "password_hash": hashed_password,
            "role": role,
            "is_approved": is_approved,
            "created_at": datetime.utcnow(),
            "phone": "",
            "about_me": "",
            "city": "",
            "country": "",
            "languages": "",
            "gender": "",
            "profile_picture": None
        }
        
        # Insert into MongoDB
        result = users.insert_one(user_doc)
        user_id = str(result.inserted_id)
        
        # Publish event to Kafka (non-blocking)
        try:
            producer = get_producer()
            producer.publish_event(
                topic="user.created",
                event={
                    "user_id": user_id,
                    "name": user.name,
                    "email": user.email,
                    "role": role,
                    "timestamp": datetime.utcnow().isoformat()
                },
                key=user_id
            )
        except Exception as kafka_err:
            logger.warning(f"⚠️ Kafka unavailable, skipping event: {kafka_err}")
        
        # Create JWT token
        token = create_access_token({
            "sub": user_id,
            "role": role,
            "is_approved": is_approved
        })
        
        logger.info(f"✅ User created: {user.email}")
        
        return {
            "message": "User created successfully",
            "token": token,
            "user": {
                "id": user_id,
                "name": user.name,
                "email": user.email,
                "role": role,
                "is_approved": is_approved
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
async def login(user: LoginRequest):
    """User login - bcrypt runs in thread pool to avoid blocking event loop"""
    try:
        users = get_users_collection()
        
        # Find user
        db_user = users.find_one({"email": user.email})
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password - run bcrypt in thread pool so it doesn't block event loop
        stored_hash = db_user.get("password_hash") or db_user.get("password")
        if not stored_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        loop = asyncio.get_event_loop()
        password_valid = await loop.run_in_executor(
            _executor,
            bcrypt.checkpw,
            user.password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )

        if not password_valid:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create JWT token
        token = create_access_token({
            "sub": str(db_user["_id"]),
            "role": db_user["role"],
            "is_approved": db_user.get("is_approved", True)
        })
        
        # Publish login event (non-blocking)
        try:
            producer = get_producer()
            producer.publish_event(
                topic="user.login",
                event={
                    "user_id": str(db_user["_id"]),
                    "email": user.email,
                    "timestamp": datetime.utcnow().isoformat()
                },
                key=str(db_user["_id"])
            )
        except Exception as kafka_err:
            logger.warning(f"⚠️ Kafka unavailable, skipping event: {kafka_err}")
        
        logger.info(f"✅ User logged in: {user.email}")
        
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": str(db_user["_id"]),
                "name": db_user["name"],
                "email": db_user["email"],
                "role": db_user["role"],
                "is_approved": db_user.get("is_approved", True)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}")
def get_user(user_id: str):
    """Get user profile"""
    try:
        users = get_users_collection()
        user = users.find_one({"_id": ObjectId(user_id)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["id"] = str(user.pop("_id"))
        user.pop("password_hash", None)
        
        return user
        
    except Exception as e:
        logger.error(f"❌ Get user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/users/{user_id}")
def update_user(user_id: str, update: UserProfileUpdate):
    """Update user profile - publish event to Kafka"""
    try:
        users = get_users_collection()
        
        result = users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "name": update.name,
                "phone": update.phone,
                "about_me": update.about_me,
                "city": update.city,
                "country": update.country,
                "languages": update.languages,
                "gender": update.gender,
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Publish event to Kafka (non-blocking)
        try:
            producer = get_producer()
            producer.publish_event(
                topic="user.updated",
                event={
                    "user_id": user_id,
                    "name": update.name,
                    "city": update.city,
                    "country": update.country,
                    "timestamp": datetime.utcnow().isoformat()
                },
                key=user_id
            )
        except Exception as kafka_err:
            logger.warning(f"⚠️ Kafka unavailable, skipping event: {kafka_err}")
        
        logger.info(f"✅ User updated: {user_id}")
        
        return {"message": "Profile updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
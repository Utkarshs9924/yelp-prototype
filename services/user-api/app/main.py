"""
User API Service - Producer
Handles user authentication and profile management
Publishes events to Kafka for async processing
"""
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import bcrypt
import jwt
from datetime import datetime, timedelta
from common.kafka import get_producer
from common.database import get_users_collection, get_sessions_collection
from common.utils.s3_storage import upload_to_s3
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="User API Service")

_executor = ThreadPoolExecutor(max_workers=10)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET = os.getenv("JWT_SECRET", "akash_yelp_lab_secret_key_2024_!@#")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24


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


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_id_from_token(authorization: str) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    payload = verify_token(token)
    return payload.get("sub")


@app.get("/")
def root():
    return {"service": "User API", "status": "running"}


@app.post("/signup")
def signup(user: SignupRequest):
    try:
        users = get_users_collection()
        if users.find_one({"email": user.email}):
            raise HTTPException(status_code=400, detail="Email already registered")

        hashed_password = bcrypt.hashpw(
            user.password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

        role = user.role if user.role in ["user", "owner"] else "user"
        is_approved = role == "user"

        user_doc = {
            "name": user.name,
            "email": user.email,
            "password_hash": hashed_password,
            "role": role,
            "is_approved": is_approved,
            "created_at": datetime.utcnow(),
            "phone": "", "about_me": "", "city": "", "country": "",
            "languages": "", "gender": "", "profile_picture": None
        }

        result = users.insert_one(user_doc)
        user_id = str(result.inserted_id)

        try:
            get_producer().publish_event(
                topic="user.created",
                event={"user_id": user_id, "name": user.name, "email": user.email,
                       "role": role, "timestamp": datetime.utcnow().isoformat()},
                key=user_id
            )
        except Exception as e:
            logger.warning(f"⚠️ Kafka unavailable: {e}")

        token = create_access_token({"sub": user_id, "role": role, "is_approved": is_approved})
        logger.info(f"✅ User created: {user.email}")

        return {
            "message": "User created successfully", "token": token,
            "user": {"id": user_id, "name": user.name, "email": user.email,
                     "role": role, "is_approved": is_approved}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Signup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
async def login(user: LoginRequest):
    try:
        users = get_users_collection()
        db_user = users.find_one({"email": user.email})
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        stored_hash = db_user.get("password_hash") or db_user.get("password")
        if not stored_hash:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        loop = asyncio.get_event_loop()
        password_valid = await loop.run_in_executor(
            _executor, bcrypt.checkpw,
            user.password.encode('utf-8'), stored_hash.encode('utf-8')
        )
        if not password_valid:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token({
            "sub": str(db_user["_id"]),
            "role": db_user["role"],
            "is_approved": db_user.get("is_approved", True)
        })

        try:
            get_producer().publish_event(
                topic="user.login",
                event={"user_id": str(db_user["_id"]), "email": user.email,
                       "timestamp": datetime.utcnow().isoformat()},
                key=str(db_user["_id"])
            )
        except Exception as e:
            logger.warning(f"⚠️ Kafka unavailable: {e}")

        logger.info(f"✅ User logged in: {user.email}")
        return {
            "message": "Login successful", "token": token,
            "user": {"id": str(db_user["_id"]), "name": db_user["name"],
                     "email": db_user["email"], "role": db_user["role"],
                     "is_approved": db_user.get("is_approved", True)}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/users/{user_id}")
def get_user(user_id: str):
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
    try:
        users = get_users_collection()
        result = users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "name": update.name, "phone": update.phone,
                "about_me": update.about_me, "city": update.city,
                "country": update.country, "languages": update.languages,
                "gender": update.gender, "updated_at": datetime.utcnow()
            }}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            get_producer().publish_event(
                topic="user.updated",
                event={"user_id": user_id, "name": update.name,
                       "city": update.city, "country": update.country,
                       "timestamp": datetime.utcnow().isoformat()},
                key=user_id
            )
        except Exception as e:
            logger.warning(f"⚠️ Kafka unavailable: {e}")

        logger.info(f"✅ User updated: {user_id}")
        return {"message": "Profile updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Update user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/users/upload-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    authorization: str = Header(None)
):
    """Upload profile picture to S3 and update user record"""
    user_id = get_user_id_from_token(authorization)
    try:
        contents = await file.read()
        photo_url = await upload_to_s3(
            contents, file.filename, file.content_type, folder="profile-pictures"
        )
        users = get_users_collection()
        users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_picture": photo_url, "updated_at": datetime.utcnow()}}
        )
        logger.info(f"✅ Profile picture updated for user {user_id}")
        return {"message": "Profile picture updated", "photo_url": photo_url}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Upload profile picture error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
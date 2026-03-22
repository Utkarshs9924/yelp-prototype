from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from database import get_db_connection
import bcrypt
from auth import create_access_token, get_current_user
from utils.blob_storage import upload_to_blob

router = APIRouter(tags=["Users"])


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
    phone: str
    about_me: str
    city: str
    country: str
    languages: str
    gender: str


@router.post("/signup")
def signup(user: SignupRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    role = user.role if user.role in ["user", "owner"] else "user"
    is_approved = True if role == "user" else False

    query = "INSERT INTO users (name, email, password_hash, role, is_approved) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(query, (user.name, user.email, hashed_password, role, is_approved))

    conn.commit()
    conn.close()

    return {"message": "User created successfully"}


@router.post("/login")
def login(user: LoginRequest):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (user.email,))
    db_user = cursor.fetchone()

    conn.close()

    if not db_user:
        return {"message": "User not found"}

    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user["password_hash"].encode('utf-8')):
        return {"message": "Invalid password"}

    token = create_access_token({
        "sub": str(db_user["id"]), 
        "role": db_user["role"], 
        "is_approved": db_user["is_approved"]
    })
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": db_user["id"],
            "name": db_user["name"],
            "email": db_user["email"],
            "role": db_user["role"],
            "is_approved": db_user["is_approved"]
        }
    }


@router.get("/users/{user_id}")
def get_user(user_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))

    user = cursor.fetchone()

    conn.close()

    return user


@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserProfileUpdate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    UPDATE users
    SET name=%s,
        phone=%s,
        about_me=%s,
        city=%s,
        country=%s,
        languages=%s,
        gender=%s
    WHERE id=%s
    """

    cursor.execute((
        query
    ), (
        user.name,
        user.phone,
        user.about_me,
        user.city,
        user.country,
        user.languages,
        user.gender,
        user_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Profile updated successfully"}


@router.post("/users/upload-picture")
async def upload_user_picture(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, and GIF images are allowed")
    
    # Max 5MB for profile pics
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 5MB")

    # Upload to Azure Blob Storage using utility (folder = avatars)
    photo_url = await upload_to_blob(contents, file.filename, file.content_type, folder="avatars")
    
    try:
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET profile_picture = %s WHERE id = %s",
            (photo_url, user['id'])
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"FAILED SQL Update Profile Pic: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {"profile_picture": photo_url, "message": "Profile picture updated"}


@router.get("/users/{user_id}/reviews")
def get_user_reviews(user_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM reviews WHERE user_id = %s"

    cursor.execute(query, (user_id,))
    reviews = cursor.fetchall()

    conn.close()

    return reviews


@router.get("/users/{user_id}/restaurants")
def get_user_restaurants(user_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM restaurants WHERE created_by_user_id = %s"

    cursor.execute(query, (user_id,))
    restaurants = cursor.fetchall()

    conn.close()

    return restaurants
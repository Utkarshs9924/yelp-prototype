from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from database import get_db_connection
from auth import get_current_user
from utils.blob_storage import upload_to_blob

router = APIRouter(tags=["Reviews"])


class ReviewCreate(BaseModel):
    restaurant_id: int
    rating: int
    comment: Optional[str] = None
    photo_url: Optional[str] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None


@router.post("/reviews/upload-photo")
async def upload_review_photo(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, and GIF images are allowed")
    
    # Max 5MB
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 5MB")

    # Upload to Azure Blob Storage (folder = reviews)
    photo_url = await upload_to_blob(contents, file.filename, file.content_type, folder="reviews")
    return {"photo_url": photo_url}


@router.post("/reviews")
def create_review(review: ReviewCreate, user: dict = Depends(get_current_user)):
    uid = user["id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO reviews (user_id, restaurant_id, rating, comment, photo_url)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (uid, review.restaurant_id, review.rating, review.comment, review.photo_url))
    review_id = cursor.lastrowid

    # Sync with 'photos' table if photo exists
    if review.photo_url:
        cursor.execute("""
            INSERT INTO photos (restaurant_id, review_id, user_id, photo_url, caption)
            VALUES (%s, %s, %s, %s, %s)
        """, (review.restaurant_id, review_id, uid, review.photo_url, f"Photo by {user.get('name', 'User')}"))

    conn.commit()
    conn.close()

    return {"message": "Review created successfully"}


@router.get("/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(restaurant_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT reviews.id, reviews.user_id, reviews.rating, reviews.comment,
           reviews.photo_url, reviews.created_at, users.name as user_name
    FROM reviews
    JOIN users ON reviews.user_id = users.id
    WHERE reviews.restaurant_id = %s
    ORDER BY reviews.created_at DESC
    """
    cursor.execute(query, (restaurant_id,))
    reviews = cursor.fetchall()

    conn.close()
    return reviews


@router.put("/reviews/{review_id}")
def update_review(review_id: int, review: ReviewUpdate, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if review exists
    cursor.execute("SELECT user_id, restaurant_id FROM reviews WHERE id = %s", (review_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check authorization: Admin or Restaurant Owner
    is_admin = user.get("role") == "admin"
    
    # Check if user is the approved owner of this specific restaurant
    cursor.execute("SELECT owner_id FROM restaurants WHERE id = %s", (existing["restaurant_id"],))
    restaurant = cursor.fetchone()
    is_owner = user.get("role") == "owner" and restaurant and restaurant["owner_id"] == user["id"]

    if not (is_admin or is_owner):
        conn.close()
        raise HTTPException(status_code=403, detail="Only admins and restaurant owners can edit reviews")

    updates = []
    params = []
    if review.rating is not None:
        updates.append("rating = %s")
        params.append(review.rating)
    if review.comment is not None:
        updates.append("comment = %s")
        params.append(review.comment)

    if not updates:
        conn.close()
        return {"message": "Nothing to update"}

    params.append(review_id)
    query = f"UPDATE reviews SET {', '.join(updates)} WHERE id = %s"
    cursor.execute(query, tuple(params))

    conn.commit()
    conn.close()
    return {"message": "Review updated successfully"}


@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if review exists
    cursor.execute("SELECT user_id, restaurant_id FROM reviews WHERE id = %s", (review_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Check authorization: Admin or Restaurant Owner
    is_admin = user.get("role") == "admin"
    
    # Check if user is the approved owner of this specific restaurant
    cursor.execute("SELECT owner_id FROM restaurants WHERE id = %s", (existing["restaurant_id"],))
    restaurant = cursor.fetchone()
    is_owner = user.get("role") == "owner" and restaurant and restaurant["owner_id"] == user["id"]

    if not (is_admin or is_owner):
        conn.close()
        raise HTTPException(status_code=403, detail="Only admins and restaurant owners can delete reviews")

    cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
    conn.commit()
    conn.close()

    return {"message": "Review deleted successfully"}

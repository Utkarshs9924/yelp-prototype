from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db_connection
from auth import get_current_user

router = APIRouter(tags=["Reviews"])


class ReviewCreate(BaseModel):
    restaurant_id: int
    rating: int
    comment: Optional[str] = None
    user_id: Optional[int] = None


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    comment: Optional[str] = None


@router.post("/reviews")
def create_review(review: ReviewCreate, user: dict = Depends(get_current_user)):
    uid = user["id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO reviews (user_id, restaurant_id, rating, comment)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (uid, review.restaurant_id, review.rating, review.comment))

    conn.commit()
    conn.close()

    return {"message": "Review created successfully"}


@router.get("/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(restaurant_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT reviews.id, reviews.user_id, reviews.rating, reviews.comment,
           reviews.created_at, users.name as user_name
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

    cursor.execute("SELECT user_id FROM reviews WHERE id = %s", (review_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Review not found")
    if existing["user_id"] != user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="You can only edit your own reviews")

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

    cursor.execute("SELECT user_id FROM reviews WHERE id = %s", (review_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Review not found")
    if existing["user_id"] != user["id"]:
        conn.close()
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")

    cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
    conn.commit()
    conn.close()

    return {"message": "Review deleted successfully"}

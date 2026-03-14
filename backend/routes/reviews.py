from fastapi import APIRouter
from pydantic import BaseModel
from database import get_db_connection

router = APIRouter()

router = APIRouter(tags=["Reviews"])


class ReviewCreate(BaseModel):
    user_id: int
    restaurant_id: int
    rating: int
    comment: str


class ReviewUpdate(BaseModel):
    rating: int
    comment: str


@router.post("/reviews")
def create_review(review: ReviewCreate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO reviews (user_id, restaurant_id, rating, comment)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (
        review.user_id,
        review.restaurant_id,
        review.rating,
        review.comment
    ))

    conn.commit()
    conn.close()

    return {"message": "Review created successfully"}


@router.get("/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(restaurant_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT reviews.id, reviews.rating, reviews.comment, reviews.review_date,
           users.name as user_name
    FROM reviews
    JOIN users ON reviews.user_id = users.id
    WHERE reviews.restaurant_id = %s
    """

    cursor.execute(query, (restaurant_id,))
    reviews = cursor.fetchall()

    conn.close()

    return reviews


@router.put("/reviews/{review_id}")
def update_review(review_id: int, review: ReviewUpdate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    UPDATE reviews
    SET rating = %s, comment = %s
    WHERE id = %s
    """

    cursor.execute(query, (
        review.rating,
        review.comment,
        review_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Review updated successfully"}


@router.delete("/reviews/{review_id}")
def delete_review(review_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "DELETE FROM reviews WHERE id = %s"
    cursor.execute(query, (review_id,))

    conn.commit()
    conn.close()

    return {"message": "Review deleted successfully"}
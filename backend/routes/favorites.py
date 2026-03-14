from fastapi import APIRouter
from pydantic import BaseModel
from database import get_db_connection

router = APIRouter()

router = APIRouter(tags=["Favorites"])


class FavoriteCreate(BaseModel):
    user_id: int
    restaurant_id: int


@router.post("/favorites")
def add_favorite(favorite: FavoriteCreate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO favorites (user_id, restaurant_id)
    VALUES (%s, %s)
    """

    cursor.execute(query, (
        favorite.user_id,
        favorite.restaurant_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Restaurant added to favorites"}


@router.get("/favorites/{user_id}")
def get_favorites(user_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT restaurants.*
    FROM favorites
    JOIN restaurants ON favorites.restaurant_id = restaurants.id
    WHERE favorites.user_id = %s
    """

    cursor.execute(query, (user_id,))
    favorites = cursor.fetchall()

    conn.close()

    return favorites


@router.delete("/favorites/{favorite_id}")
def remove_favorite(favorite_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "DELETE FROM favorites WHERE id = %s"
    cursor.execute(query, (favorite_id,))

    conn.commit()
    conn.close()

    return {"message": "Favorite removed"}
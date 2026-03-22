from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db_connection
from auth import get_current_user

router = APIRouter(tags=["Favorites"])


@router.post("/favorites")
def add_favorite(data: dict, user: dict = Depends(get_current_user)):
    restaurant_id = data.get("restaurant_id")
    if not restaurant_id:
        raise HTTPException(status_code=400, detail="restaurant_id is required")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM favourites WHERE user_id = %s AND restaurant_id = %s",
        (user["id"], restaurant_id)
    )
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=409, detail="Already in favourites")

    cursor.execute(
        "INSERT INTO favourites (user_id, restaurant_id) VALUES (%s, %s)",
        (user["id"], restaurant_id)
    )
    conn.commit()
    conn.close()

    return {"message": "Restaurant added to favourites"}


@router.get("/favorites")
def get_favorites(user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT r.*, GROUP_CONCAT(rp.photo_url) as photos_str
    FROM favourites f
    JOIN restaurants r ON f.restaurant_id = r.id
    LEFT JOIN restaurant_photos rp ON r.id = rp.restaurant_id
    WHERE f.user_id = %s
    GROUP BY r.id
    """
    cursor.execute(query, (user["id"],))
    favorites = cursor.fetchall()

    for fav in favorites:
        fav['photos'] = fav['photos_str'].split(',') if fav.get('photos_str') else []
        fav.pop('photos_str', None)

    conn.close()
    return favorites


@router.get("/favorites/check/{restaurant_id}")
def check_favorite(restaurant_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id FROM favourites WHERE user_id = %s AND restaurant_id = %s",
        (user["id"], restaurant_id)
    )
    row = cursor.fetchone()
    conn.close()

    return {"is_favourite": row is not None}


@router.delete("/favorites/{restaurant_id}")
def remove_favorite(restaurant_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM favourites WHERE user_id = %s AND restaurant_id = %s",
        (user["id"], restaurant_id)
    )
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Favourite not found")

    conn.commit()
    conn.close()
    return {"message": "Favourite removed"}

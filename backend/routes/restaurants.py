from fastapi import APIRouter
from pydantic import BaseModel
from database import get_db_connection

router = APIRouter()

router = APIRouter(tags=["Restaurants"])


class RestaurantCreate(BaseModel):
    name: str
    cuisine_type: str
    address: str
    city: str
    description: str
    contact_info: str
    price_tier: str
    user_id: int


@router.post("/restaurants")
def create_restaurant(restaurant: RestaurantCreate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO restaurants
    (name, cuisine_type, address, city, description, contact_info, price_tier, created_by_user_id)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (
        restaurant.name,
        restaurant.cuisine_type,
        restaurant.address,
        restaurant.city,
        restaurant.description,
        restaurant.contact_info,
        restaurant.price_tier,
        restaurant.user_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Restaurant created successfully"}


@router.get("/restaurants")
def get_restaurants():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM restaurants")

    restaurants = cursor.fetchall()

    conn.close()

    return restaurants


@router.get("/restaurants/search")
def search_restaurants(
    name: str = None,
    cuisine: str = None,
    city: str = None
):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM restaurants WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE %s"
        params.append(f"%{name}%")

    if cuisine:
        query += " AND cuisine_type LIKE %s"
        params.append(f"%{cuisine}%")

    if city:
        query += " AND city LIKE %s"
        params.append(f"%{city}%")

    cursor.execute(query, tuple(params))
    restaurants = cursor.fetchall()

    conn.close()

    return restaurants


@router.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM restaurants WHERE id = %s"
    cursor.execute(query, (restaurant_id,))

    restaurant = cursor.fetchone()

    conn.close()

    return restaurant
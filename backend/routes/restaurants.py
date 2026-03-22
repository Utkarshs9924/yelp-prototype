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

    query = """
    SELECT r.*,
           GROUP_CONCAT(rp.photo_url) as photos_str,
           COALESCE((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.restaurant_id = r.id), 0) as average_rating,
           COALESCE((SELECT COUNT(*) FROM reviews rv WHERE rv.restaurant_id = r.id), 0) as review_count
    FROM restaurants r
    LEFT JOIN restaurant_photos rp ON r.id = rp.restaurant_id
    GROUP BY r.id
    """
    cursor.execute(query)

    restaurants = cursor.fetchall()
    
    for r in restaurants:
        r['photos'] = r['photos_str'].split(',') if r.get('photos_str') else []
        r.pop('photos_str', None)

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

    query = """
    SELECT r.*,
           GROUP_CONCAT(rp.photo_url) as photos_str,
           COALESCE((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.restaurant_id = r.id), 0) as average_rating,
           COALESCE((SELECT COUNT(*) FROM reviews rv WHERE rv.restaurant_id = r.id), 0) as review_count
    FROM restaurants r
    LEFT JOIN restaurant_photos rp ON r.id = rp.restaurant_id
    WHERE 1=1
    """
    params = []

    if name:
        query += " AND r.name LIKE %s"
        params.append(f"%{name}%")

    if cuisine:
        query += " AND r.cuisine_type LIKE %s"
        params.append(f"%{cuisine}%")

    if city:
        query += " AND r.city LIKE %s"
        params.append(f"%{city}%")

    query += " GROUP BY r.id"

    cursor.execute(query, tuple(params))
    restaurants = cursor.fetchall()
    
    for r in restaurants:
        r['photos'] = r['photos_str'].split(',') if r.get('photos_str') else []
        r.pop('photos_str', None)

    conn.close()

    return restaurants


@router.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT r.*,
           COALESCE((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.restaurant_id = r.id), 0) as average_rating,
           COALESCE((SELECT COUNT(*) FROM reviews rv WHERE rv.restaurant_id = r.id), 0) as review_count
    FROM restaurants r
    WHERE r.id = %s
    """
    cursor.execute(query, (restaurant_id,))

    restaurant = cursor.fetchone()
    
    if restaurant:
        # Fetch photos with IDs separately for proper delete support
        cursor.execute("SELECT id, photo_url FROM restaurant_photos WHERE restaurant_id = %s", (restaurant_id,))
        photo_rows = cursor.fetchall()
        restaurant['photos'] = [p['photo_url'] for p in photo_rows]
        restaurant['photo_ids'] = [p['id'] for p in photo_rows]

    conn.close()

    return restaurant


@router.get("/restaurants/{restaurant_id}/menu")
def get_restaurant_menu(restaurant_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, name, description, price
        FROM menu_items
        WHERE restaurant_id = %s
        ORDER BY price ASC
    """, (restaurant_id,))

    items = cursor.fetchall()
    conn.close()

    return items
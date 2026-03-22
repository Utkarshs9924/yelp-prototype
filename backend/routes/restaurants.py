from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db_connection
from auth import get_current_user

router = APIRouter(tags=["Restaurants"])


class RestaurantCreate(BaseModel):
    name: str
    cuisine_type: str = None
    description: str = None
    address: str = None
    city: str = None
    state: str = None
    zip_code: str = None
    phone: str = None
    email: str = None
    website: str = None
    hours_of_operation: str = None
    pricing_tier: str = None
    amenities: str = None
    ambiance: str = None


@router.post("/restaurants")
def create_restaurant(restaurant: RestaurantCreate, user: dict = Depends(get_current_user)):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO restaurants
    (name, cuisine_type, description, address, city, state, zip_code, phone, email, website, hours_of_operation, pricing_tier, amenities, ambiance, created_by)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (
        restaurant.name,
        restaurant.cuisine_type,
        restaurant.description,
        restaurant.address,
        restaurant.city,
        restaurant.state,
        restaurant.zip_code,
        restaurant.phone,
        restaurant.email,
        restaurant.website,
        restaurant.hours_of_operation,
        restaurant.pricing_tier,
        restaurant.amenities,
        restaurant.ambiance,
        user['id']
    ))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"message": "Restaurant created successfully", "id": new_id}



@router.get("/restaurants")
def get_restaurants():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT r.id, r.name, r.cuisine_type, r.description, r.address, r.city, r.state, r.zip_code, r.phone, r.email, r.website, r.hours_of_operation, r.pricing_tier, r.amenities, r.ambiance, r.owner_id, r.created_by, r.created_at, r.updated_at, r.status, r.views,
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
    city: str = None,
    pricing_tier: str = None,
    zip_code: str = None
):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT r.id, r.name, r.cuisine_type, r.description, r.address, r.city, r.state, r.zip_code, r.phone, r.email, r.website, r.hours_of_operation, r.pricing_tier, r.amenities, r.ambiance, r.owner_id, r.created_by, r.created_at, r.updated_at, r.status, r.views,
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

    if pricing_tier:
        query += " AND r.price_tier = %s"
        params.append(pricing_tier)

    if zip_code:
        query += " AND r.address LIKE %s"
        params.append(f"%{zip_code}%")

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
    # Increment view count
    cursor.execute("UPDATE restaurants SET views = views + 1 WHERE id = %s", (restaurant_id,))
    conn.commit()

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


@router.post("/restaurants/{restaurant_id}/claim")
def claim_restaurant(restaurant_id: int, user: dict = Depends(get_current_user)):
    """
    Allow an authenticated owner to claim a restaurant that has no owner assigned.
    The claim will be set to 'pending' state for admin approval.
    """
    if user.get("role") != "owner":
        raise HTTPException(status_code=403, detail="Only users with the 'owner' role can claim restaurants")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # 1. Check if restaurant exists and if it's already claimed
    cursor.execute("SELECT owner_id, name FROM restaurants WHERE id = %s", (restaurant_id,))
    res = cursor.fetchone()

    if not res:
        conn.close()
        raise HTTPException(status_code=404, detail="Restaurant not found")

    if res['owner_id'] is not None:
        conn.close()
        raise HTTPException(status_code=400, detail="This restaurant is already claimed by another owner")

    # 2. Update owner_id and set status to pending for admin approval
    cursor.execute(
        "UPDATE restaurants SET owner_id = %s, status = 'pending' WHERE id = %s",
        (user['id'], restaurant_id)
    )

    conn.commit()
    conn.close()

    return {"message": f"Claim request for '{res['name']}' submitted successfully and is pending admin approval."}
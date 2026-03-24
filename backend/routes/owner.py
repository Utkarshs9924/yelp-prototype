from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_db_connection
from auth import get_current_user, require_role

router = APIRouter(prefix="/owner", tags=["Owner"])

@router.get("/restaurants")
def get_owner_restaurants(user: dict = Depends(require_role(["owner", "admin"]))):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restaurants WHERE owner_id = %s", (user["id"],))
    restaurants = cursor.fetchall()
    conn.close()
    return restaurants

@router.get("/dashboard")
def get_owner_dashboard(user: dict = Depends(require_role(["owner", "admin"]))):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Get all restaurants owned by the user
    cursor.execute("SELECT id, name, views FROM restaurants WHERE owner_id = %s", (user["id"],))
    restaurants = cursor.fetchall()
    
    dashboard = {
        "total_restaurants": len(restaurants),
        "total_reviews": 0,
        "total_views": sum(r["views"] or 0 for r in restaurants),
        "overall_average_rating": 0.0,
        "restaurants": []
    }
    
    if not restaurants:
        conn.close()
        return dashboard

    total_rating_sum = 0
    total_review_count = 0
    
    for r in restaurants:
        r_id = r["id"]
        
        # Get reviews for this restaurant
        cursor.execute("""
            SELECT r.rating, r.comment, r.created_at, u.name as user_name 
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.restaurant_id = %s
            ORDER BY r.created_at DESC
        """, (r_id,))
        reviews = cursor.fetchall()
        
        review_count = len(reviews)
        sum_ratings = sum(rev["rating"] for rev in reviews)
        avg_rating = sum_ratings / review_count if review_count > 0 else 0
        
        # Sentiment Index: % of 4-5 star reviews
        positive_reviews = sum(1 for rev in reviews if rev["rating"] >= 4)
        sentiment_index = (positive_reviews / review_count * 100) if review_count > 0 else 0
        
        rating_dist = {5:0, 4:0, 3:0, 2:0, 1:0}
        for rev in reviews:
            if rev["rating"] in rating_dist:
                rating_dist[rev["rating"]] += 1
                
        dashboard["restaurants"].append({
            "id": r_id,
            "name": r["name"],
            "views": r["views"] or 0,
            "average_rating": avg_rating,
            "sentiment_index": round(sentiment_index, 1),
            "review_count": review_count,
            "rating_distribution": rating_dist,
            "recent_reviews": reviews[:5]  # Last 5 reviews
        })
        
        total_rating_sum += sum_ratings
        total_review_count += review_count
        
    dashboard["total_reviews"] = total_review_count
    dashboard["overall_average_rating"] = round(total_rating_sum / total_review_count, 1) if total_review_count > 0 else 0.0
    
    conn.close()
    return dashboard

class RestaurantCreate(BaseModel):
    name: str
    cuisine_type: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    
@router.post("/restaurants")
def submit_new_restaurant(req: RestaurantCreate, user: dict = Depends(require_role(["owner"]))):
    if not user.get("is_approved"):
        raise HTTPException(status_code=403, detail="Your owner profile is pending approval by an admin.")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO restaurants (name, cuisine_type, description, address, city, state, zip_code, owner_id, status)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')
    """
    cursor.execute(query, (
        req.name, req.cuisine_type, req.description, req.address, req.city, req.state, req.zip_code, 
        user["id"]
    ))
    conn.commit()
    conn.close()
    return {"message": "Restaurant submitted for approval"}

@router.get("/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(restaurant_id: int, user: dict = Depends(require_role(["owner", "admin"]))):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if user["role"] == "owner":
        cursor.execute("SELECT id FROM restaurants WHERE id = %s AND owner_id = %s", (restaurant_id, user["id"]))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=403, detail="You do not own this restaurant")
            
    cursor.execute("""
        SELECT r.*, u.name as user_name 
        FROM reviews r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.restaurant_id = %s
    """, (restaurant_id,))
    reviews = cursor.fetchall()
    conn.close()
    return reviews

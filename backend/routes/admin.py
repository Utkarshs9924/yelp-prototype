from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import get_db_connection
from auth import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/owners/pending")
def get_pending_owners(user: dict = Depends(require_role(["admin"]))):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, created_at FROM users WHERE role = 'owner' AND is_approved = FALSE")
    owners = cursor.fetchall()
    conn.close()
    return owners

@router.put("/owners/{owner_id}/approve")
def approve_owner(owner_id: int, user: dict = Depends(require_role(["admin"]))):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_approved = TRUE WHERE id = %s AND role = 'owner'", (owner_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Pending owner not found")
    conn.commit()
    conn.close()
    return {"message": "Owner approved successfully"}

@router.get("/restaurants/pending")
def get_pending_restaurants(user: dict = Depends(require_role(["admin"]))):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restaurants WHERE status = 'pending'")
    restaurants = cursor.fetchall()
    conn.close()
    return restaurants

class RestaurantStatusUpdate(BaseModel):
    status: str

@router.put("/restaurants/{restaurant_id}/status")
def update_restaurant_status(restaurant_id: int, update: RestaurantStatusUpdate, user: dict = Depends(require_role(["admin"]))):
    if update.status not in ['approved', 'rejected']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE restaurants SET status = %s WHERE id = %s", (update.status, restaurant_id))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Restaurant not found")
    conn.commit()
    conn.close()
    return {"message": f"Restaurant {update.status} successfully"}

class AssignOwnerUpdate(BaseModel):
    owner_id: int

@router.put("/restaurants/{restaurant_id}/assign")
def assign_restaurant_owner(restaurant_id: int, assign: AssignOwnerUpdate, user: dict = Depends(require_role(["admin"]))):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE id = %s AND role = 'owner' AND is_approved = TRUE", (assign.owner_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid or unapproved owner ID")
        
    cursor.execute("UPDATE restaurants SET owner_id = %s WHERE id = %s", (assign.owner_id, restaurant_id))
    conn.commit()
    conn.close()
    return {"message": "Owner assigned successfully"}
    
@router.put("/restaurants/{restaurant_id}/deassign")
def deassign_restaurant_owner(restaurant_id: int, user: dict = Depends(require_role(["admin"]))):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE restaurants SET owner_id = NULL WHERE id = %s", (restaurant_id,))
    conn.commit()
    conn.close()
    return {"message": "Owner deassigned successfully"}

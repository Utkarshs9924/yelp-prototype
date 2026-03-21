from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
import json
from database import get_db_connection
from auth import get_current_user

router = APIRouter(tags=["Preferences"])

class PreferencesPayload(BaseModel):
    cuisine_preferences: List[str] = []
    price_range: str = ""
    preferred_locations: List[str] = []
    search_radius: int = 10
    dietary_needs: List[str] = []
    ambiance_preferences: List[str] = []
    sort_preference: str = "Rating"

@router.get("/preferences")
def get_preferences(user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM preferences WHERE user_id = %s", (user["id"],))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {}
        
    # parse JSON or return defaults
    return {
        "cuisine_preferences": json.loads(row["cuisine_preferences"]) if row["cuisine_preferences"] else [],
        "price_range": row["price_range"],
        "preferred_locations": json.loads(row["preferred_locations"]) if row["preferred_locations"] else [],
        "search_radius": row["search_radius"],
        "dietary_needs": json.loads(row["dietary_needs"]) if row["dietary_needs"] else [],
        "ambiance_preferences": json.loads(row["ambiance_preferences"]) if row["ambiance_preferences"] else [],
        "sort_preference": row["sort_preference"]
    }

@router.put("/preferences")
def update_preferences(data: PreferencesPayload, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM preferences WHERE user_id = %s", (user["id"],))
    exists = cursor.fetchone()
    
    if exists:
        query = """
        UPDATE preferences
        SET cuisine_preferences=%s,
            price_range=%s,
            preferred_locations=%s,
            search_radius=%s,
            dietary_needs=%s,
            ambiance_preferences=%s,
            sort_preference=%s
        WHERE user_id=%s
        """
        cursor.execute(query, (
            json.dumps(data.cuisine_preferences),
            data.price_range,
            json.dumps(data.preferred_locations),
            data.search_radius,
            json.dumps(data.dietary_needs),
            json.dumps(data.ambiance_preferences),
            data.sort_preference,
            user["id"]
        ))
    else:
        query = """
        INSERT INTO preferences
        (user_id, cuisine_preferences, price_range, preferred_locations, search_radius, dietary_needs, ambiance_preferences, sort_preference)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(query, (
            user["id"],
            json.dumps(data.cuisine_preferences),
            data.price_range,
            json.dumps(data.preferred_locations),
            data.search_radius,
            json.dumps(data.dietary_needs),
            json.dumps(data.ambiance_preferences),
            data.sort_preference
        ))
        
    conn.commit()
    conn.close()
    return {"message": "Preferences saved successfully"}
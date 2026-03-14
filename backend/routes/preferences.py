from fastapi import APIRouter
from pydantic import BaseModel
from database import get_db_connection

router = APIRouter()

router = APIRouter(tags=["Preferences"])


class PreferencesCreate(BaseModel):
    user_id: int
    cuisine_preferences: str
    price_range: str
    dietary_restrictions: str
    ambiance_preferences: str
    preferred_location: str


class PreferencesUpdate(BaseModel):
    cuisine_preferences: str
    price_range: str
    dietary_restrictions: str
    ambiance_preferences: str
    preferred_location: str


@router.post("/preferences")
def create_preferences(preferences: PreferencesCreate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO preferences
    (user_id, cuisine_preferences, price_range, dietary_restrictions, ambiance_preferences, preferred_location)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (
        preferences.user_id,
        preferences.cuisine_preferences,
        preferences.price_range,
        preferences.dietary_restrictions,
        preferences.ambiance_preferences,
        preferences.preferred_location
    ))

    conn.commit()
    conn.close()

    return {"message": "Preferences saved successfully"}


@router.get("/preferences/{user_id}")
def get_preferences(user_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM preferences WHERE user_id = %s"
    cursor.execute(query, (user_id,))

    preferences = cursor.fetchone()

    conn.close()

    return preferences


@router.put("/preferences/{user_id}")
def update_preferences(user_id: int, preferences: PreferencesUpdate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    UPDATE preferences
    SET cuisine_preferences=%s,
        price_range=%s,
        dietary_restrictions=%s,
        ambiance_preferences=%s,
        preferred_location=%s
    WHERE user_id=%s
    """

    cursor.execute(query, (
        preferences.cuisine_preferences,
        preferences.price_range,
        preferences.dietary_restrictions,
        preferences.ambiance_preferences,
        preferences.preferred_location,
        user_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Preferences updated successfully"}
from fastapi import APIRouter, Depends
from database import get_db_connection
from auth import get_current_user

router = APIRouter(tags=["History"])


@router.get("/history")
def get_history(user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            rv.id,
            'review' as type,
            rv.restaurant_id,
            r.name as restaurant_name,
            rv.rating,
            rv.comment,
            rv.created_at
        FROM reviews rv
        JOIN restaurants r ON rv.restaurant_id = r.id
        WHERE rv.user_id = %s

        UNION ALL

        SELECT 
            rest.id,
            'restaurant_added' as type,
            rest.id as restaurant_id,
            rest.name as restaurant_name,
            NULL as rating,
            NULL as comment,
            rest.created_at
        FROM restaurants rest
        WHERE rest.created_by = %s

        ORDER BY created_at DESC
    """, (user["id"], user["id"]))

    history = cursor.fetchall()
    conn.close()

    return {"history": history}

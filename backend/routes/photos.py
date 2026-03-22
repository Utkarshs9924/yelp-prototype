from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from database import get_db_connection
from auth import get_current_user
import os
from utils.blob_storage import upload_to_blob, delete_from_blob

router = APIRouter(tags=["Photos"])

@router.post("/restaurants/{restaurant_id}/photos")
async def upload_photo(
    restaurant_id: int,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/gif"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP, and GIF images are allowed")
    
    # Max 10MB
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be under 10MB")

    # Upload to Azure Blob Storage using utility
    photo_url = await upload_to_blob(contents, file.filename, file.content_type, folder=f"{restaurant_id}")
    
    try:
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO restaurant_photos (restaurant_id, photo_url, uploaded_by) VALUES (%s, %s, %s)",
            (restaurant_id, photo_url, user['id'])
        )
        photo_id = cursor.lastrowid
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"FAILED SQL Insert: {e}")
        # Cleanup blob if DB fails
        await delete_from_blob(photo_url)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {"id": photo_id, "photo_url": photo_url, "message": "Photo uploaded successfully"}

@router.delete("/photos/{photo_id}")
async def delete_photo(photo_id: int, user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch the photo record
    cursor.execute("SELECT * FROM restaurant_photos WHERE id = %s", (photo_id,))
    photo = cursor.fetchone()
    
    if not photo:
        conn.close()
        raise HTTPException(status_code=404, detail="Photo not found")
    
    # Authorization: admin, owner of the restaurant, or the uploader can delete
    is_admin = user.get('role') == 'admin'
    is_uploader = photo.get('uploaded_by') == user['id']
    
    # Check if user is owner of this restaurant
    cursor.execute("SELECT owner_id FROM restaurants WHERE id = %s", (photo['restaurant_id'],))
    restaurant = cursor.fetchone()
    is_owner = restaurant and restaurant.get('owner_id') == user['id']
    
    if not (is_admin or is_uploader or is_owner):
        conn.close()
        raise HTTPException(status_code=403, detail="You don't have permission to delete this photo")
    
    # Delete from Azure Blob Storage using utility
    await delete_from_blob(photo['photo_url'])
    
    # Delete from database
    cursor.execute("DELETE FROM restaurant_photos WHERE id = %s", (photo_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Photo deleted successfully"}

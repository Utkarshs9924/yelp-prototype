from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from database import get_db_connection
from auth import get_current_user
import os
import uuid
from azure.storage.blob import BlobServiceClient

router = APIRouter(tags=["Photos"])

def get_blob_service():
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise HTTPException(status_code=500, detail="Azure Storage not configured")
    return BlobServiceClient.from_connection_string(conn_str)

def get_container_name():
    return os.getenv("AZURE_STORAGE_CONTAINER_NAME", "restaurant-photos")


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

    # Generate unique blob name
    ext = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'jpg'
    blob_name = f"{restaurant_id}/{uuid.uuid4().hex}.{ext}"
    
    # Upload to Azure Blob Storage
    try:
        from azure.storage.blob import ContentSettings
        blob_service = get_blob_service()
        container = get_container_name()
        blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
        
        blob_client.upload_blob(contents, content_settings=ContentSettings(
            content_type=file.content_type
        ))
    except Exception as e:
        print(f"FAILED Azure Upload: {e}")
        raise HTTPException(status_code=500, detail=f"Azure Storage error: {str(e)}")


    
    # Build public URL
    photo_url = f"https://{blob_service.account_name}.blob.core.windows.net/{container}/{blob_name}"
    
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
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return {"id": photo_id, "photo_url": photo_url, "message": "Photo uploaded successfully"}



@router.delete("/photos/{photo_id}")
def delete_photo(photo_id: int, user: dict = Depends(get_current_user)):
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
    
    # Delete from Azure Blob Storage
    try:
        blob_service = get_blob_service()
        container = get_container_name()
        # Extract blob name from URL
        base_url = f"https://{blob_service.account_name}.blob.core.windows.net/{container}/"
        blob_name = photo['photo_url'].replace(base_url, '')
        blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
        blob_client.delete_blob()
    except Exception as e:
        print(f"Warning: Could not delete blob from Azure: {e}")
    
    # Delete from database
    cursor.execute("DELETE FROM restaurant_photos WHERE id = %s", (photo_id,))
    conn.commit()
    conn.close()
    
    return {"message": "Photo deleted successfully"}

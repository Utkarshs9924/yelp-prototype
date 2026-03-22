import os
import uuid
from fastapi import HTTPException
from azure.storage.blob import BlobServiceClient, ContentSettings

def get_blob_service():
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise HTTPException(status_code=500, detail="Azure Storage not configured")
    return BlobServiceClient.from_connection_string(conn_str)

def get_container_name():
    return os.getenv("AZURE_STORAGE_CONTAINER_NAME", "restaurant-photos")

async def upload_to_blob(file_contents: bytes, file_name: str, content_type: str, folder: str = "") -> str:
    """
    Uploads a file to Azure Blob Storage and returns the public URL.
    """
    try:
        blob_service = get_blob_service()
        container = get_container_name()
        
        # Generate unique blob name
        ext = file_name.rsplit('.', 1)[-1] if '.' in file_name else 'jpg'
        blob_path = f"{folder}/{uuid.uuid4().hex}.{ext}" if folder else f"{uuid.uuid4().hex}.{ext}"
        
        blob_client = blob_service.get_blob_client(container=container, blob=blob_path)
        
        blob_client.upload_blob(file_contents, content_settings=ContentSettings(
            content_type=content_type
        ))
        
        # Build public URL
        photo_url = f"https://{blob_service.account_name}.blob.core.windows.net/{container}/{blob_path}"
        return photo_url
    except Exception as e:
        print(f"FAILED Azure Upload Utility: {e}")
        raise HTTPException(status_code=500, detail=f"Azure Storage error: {str(e)}")

async def delete_from_blob(photo_url: str):
    """
    Deletes a blob from Azure Storage based on its public URL.
    """
    try:
        blob_service = get_blob_service()
        container = get_container_name()
        
        # Extract blob name from URL
        base_url = f"https://{blob_service.account_name}.blob.core.windows.net/{container}/"
        blob_name = photo_url.replace(base_url, '')
        
        blob_client = blob_service.get_blob_client(container=container, blob=blob_name)
        blob_client.delete_blob()
    except Exception as e:
        print(f"Warning: Could not delete blob from Azure: {e}")

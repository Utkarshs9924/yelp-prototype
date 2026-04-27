import os
import uuid
import boto3
from fastapi import HTTPException

def get_s3_client():
    # Uses local credentials (like ~/.aws/credentials) or env vars
    return boto3.client(
        's3',
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

def get_bucket_name():
    return os.getenv("S3_BUCKET_NAME", "yelp-restaurant-photos-akash-lab2")

async def upload_to_s3(file_contents: bytes, file_name: str, content_type: str, folder: str = "") -> str:
    """
    Uploads a file to AWS S3 and returns the public URL.
    """
    try:
        s3 = get_s3_client()
        bucket = get_bucket_name()
        
        # Generate unique name
        ext = file_name.rsplit('.', 1)[-1] if '.' in file_name else 'jpg'
        file_path = f"{folder}/{uuid.uuid4().hex}.{ext}" if folder else f"{uuid.uuid4().hex}.{ext}"
        
        s3.put_object(
            Bucket=bucket,
            Key=file_path,
            Body=file_contents,
            ContentType=content_type
        )
        
        # Build public URL
        url = f"https://{bucket}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{file_path}"
        return url
    except Exception as e:
        print(f"FAILED S3 Upload Utility: {e}")
        raise HTTPException(status_code=500, detail=f"S3 Storage error: {str(e)}")

async def delete_from_s3(photo_url: str):
    """
    Deletes an object from S3 based on its public URL.
    """
    try:
        s3 = get_s3_client()
        bucket = get_bucket_name()
        
        # Extract key from URL
        base_url = f"https://{bucket}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/"
        key = photo_url.replace(base_url, '')
        
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(f"Warning: Could not delete from S3: {e}")

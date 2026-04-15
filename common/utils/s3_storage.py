"""
AWS S3 Storage utilities for photo uploads
Replaces Azure Blob Storage from Lab 1
"""
import boto3
from botocore.exceptions import ClientError
import os
import uuid
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS S3 Configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'yelp-restaurant-photos-akash-lab2')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Initialize S3 client
s3_client = boto3.client('s3', region_name=AWS_REGION)


async def upload_to_s3(
    file_content: bytes,
    filename: str,
    content_type: str,
    folder: str = "photos"
) -> str:
    """
    Upload file to AWS S3
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        content_type: MIME type
        folder: S3 folder/prefix
    
    Returns:
        Public URL of uploaded file
    """
    try:
        # Generate unique filename
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"{folder}/{uuid.uuid4()}.{file_extension}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=unique_filename,
            Body=file_content,
            ContentType=content_type,
            ACL='public-read'  # Make publicly readable
        )
        
        # Construct public URL
        photo_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{unique_filename}"
        
        logger.info(f"✅ Uploaded to S3: {photo_url}")
        return photo_url
        
    except ClientError as e:
        logger.error(f"❌ S3 upload failed: {e}")
        raise Exception(f"Failed to upload to S3: {str(e)}")


async def delete_from_s3(photo_url: str) -> bool:
    """
    Delete file from AWS S3
    
    Args:
        photo_url: Full URL of the file
    
    Returns:
        True if successful
    """
    try:
        # Extract key from URL
        # Format: https://bucket-name.s3.region.amazonaws.com/folder/file.jpg
        key = photo_url.split(f"{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/")[-1]
        
        s3_client.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=key
        )
        
        logger.info(f"✅ Deleted from S3: {key}")
        return True
        
    except ClientError as e:
        logger.error(f"❌ S3 delete failed: {e}")
        return False


def get_presigned_url(key: str, expiration: int = 3600) -> Optional[str]:
    """
    Generate presigned URL for temporary access
    
    Args:
        key: S3 object key
        expiration: URL expiration time in seconds
    
    Returns:
        Presigned URL
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        logger.error(f"❌ Failed to generate presigned URL: {e}")
        return None

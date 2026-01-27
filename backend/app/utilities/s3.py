"""
S3 Utility Module

This module handles all interactions with AWS S3 (or LocalStack in development).
It provides functions to upload, delete, and generate URLs for files.
"""

import boto3
import os
import uuid
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# S3 Configuration from environment
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL")  # None for real AWS, URL for LocalStack
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "recipe-images")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


def get_s3_client():
    """
    Creates and returns an S3 client.
    
    Uses endpoint_url for LocalStack (local dev) or real AWS (production).
    """
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT_URL,  # None = real AWS, URL = LocalStack
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )


def ensure_bucket_exists():
    """
    Creates the S3 bucket if it doesn't exist.
    
    This is mainly needed for LocalStack since buckets don't persist
    between container restarts (unless you configure persistence).
    """
    s3 = get_s3_client()
    
    try:
        s3.head_bucket(Bucket=S3_BUCKET_NAME)
        print(f"Bucket '{S3_BUCKET_NAME}' already exists")
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code')
        if error_code == '404' or error_code == 'NoSuchBucket':
            # Bucket doesn't exist, create it
            s3.create_bucket(Bucket=S3_BUCKET_NAME)
            print(f"Created bucket '{S3_BUCKET_NAME}'")
        else:
            raise e


def generate_unique_filename(original_filename: str) -> str:
    """
    Generates a unique filename to prevent collisions.
    
    Example: "photo.jpg" -> "a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg"
    """
    # Get the file extension
    extension = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'jpg'
    
    # Generate a unique ID
    unique_id = str(uuid.uuid4())
    
    return f"{unique_id}.{extension}"


def upload_file(file_data: bytes, original_filename: str, content_type: str = "image/jpeg", folder: str = "recipes") -> str:
    """
    Uploads a file to S3 and returns the URL.
    
    Args:
        file_data: The file content as bytes
        original_filename: Original name of the file (used for extension)
        content_type: MIME type (e.g., "image/jpeg", "image/png")
        folder: The folder/prefix to store the file under (e.g., "recipes", "restaurants")
    
    Returns:
        The URL where the file can be accessed
    """
    s3 = get_s3_client()
    
    # Ensure bucket exists (important for LocalStack)
    ensure_bucket_exists()
    
    # Generate a unique filename
    filename = generate_unique_filename(original_filename)
    
    # Create the full key with folder
    key = f"{folder}/{filename}"
    
    # Upload the file
    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key=key,
        Body=file_data,
        ContentType=content_type,
        # ACL='public-read'  # Uncomment if you want public access
    )
    
    # Generate the URL
    if S3_ENDPOINT_URL:
        # LocalStack URL format
        url = f"{S3_ENDPOINT_URL}/{S3_BUCKET_NAME}/{key}"
    else:
        # Real AWS S3 URL format
        url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"
    
    return url


def delete_file(file_url: str) -> bool:
    """
    Deletes a file from S3 given its URL.
    
    Args:
        file_url: The full URL of the file to delete
    
    Returns:
        True if deleted successfully, False otherwise
    """
    s3 = get_s3_client()
    
    try:
        # Extract the filename (key) from the URL
        # URL format: http://localhost:4566/bucket-name/filename.jpg
        # or: https://bucket.s3.region.amazonaws.com/filename.jpg
        filename = file_url.rsplit('/', 1)[-1]
        
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=filename)
        return True
    except ClientError as e:
        print(f"Error deleting file: {e}")
        return False


def get_presigned_url(filename: str, expiration: int = 3600) -> str:
    """
    Generates a presigned URL for temporary access to a private file.
    
    Args:
        filename: The S3 key (filename) of the file
        expiration: URL validity in seconds (default 1 hour)
    
    Returns:
        A temporary URL that expires after the specified time
    """
    s3 = get_s3_client()
    
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': S3_BUCKET_NAME, 'Key': filename},
        ExpiresIn=expiration
    )
    
    return url

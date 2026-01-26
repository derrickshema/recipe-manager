"""
Upload routes for handling file uploads to S3.

This module handles all file upload operations. Currently supports:
- Recipe images

The pattern is: Upload file first → Get URL → Use URL when creating/updating records
This separates file handling from database operations for cleaner code.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel

from ..utilities.auth import get_current_user
from ..utilities.s3 import upload_file, delete_file
from ..models.user import User


router = APIRouter(prefix="/upload", tags=["Upload"])


# Response model for successful uploads
class UploadResponse(BaseModel):
    """Response returned after a successful file upload."""
    url: str
    filename: str
    message: str = "File uploaded successfully"


# Configuration for allowed file types and sizes
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile) -> None:
    """
    Validates that an uploaded file is an acceptable image.
    
    Checks:
    - Content type is an allowed image type
    - File size is within limits
    
    Raises:
        HTTPException: If validation fails
    """
    # Check content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # Check file size (if available)
    # Note: file.size might be None for streamed uploads
    if file.size and file.size > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_IMAGE_SIZE // (1024 * 1024)}MB"
        )


@router.post("/recipe-image", response_model=UploadResponse)
async def upload_recipe_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an image for a recipe.
    
    The uploaded image is stored in S3 under the 'recipes/' folder.
    Returns the URL which should then be used when creating/updating a recipe.
    
    Workflow:
    1. Frontend uploads image here first
    2. Gets back the S3 URL
    3. Frontend includes that URL in the recipe create/update request
    
    Args:
        file: The image file to upload (JPEG, PNG, GIF, or WebP)
        current_user: The authenticated user (ensures only logged-in users can upload)
    
    Returns:
        UploadResponse with the S3 URL and filename
    
    Raises:
        HTTPException 400: Invalid file type or file too large
        HTTPException 500: S3 upload failed
    """
    # Validate the file
    validate_image(file)
    
    # Read file content
    content = await file.read()
    
    # Double-check size after reading (in case size was None before)
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_IMAGE_SIZE // (1024 * 1024)}MB"
        )
    
    # Upload to S3
    url = upload_file(
        file_data=content,
        original_filename=file.filename or "image.jpg",
        content_type=file.content_type or "image/jpeg"
    )
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload file to storage"
        )
    
    return UploadResponse(
        url=url,
        filename=file.filename or "unknown"
    )


@router.delete("/recipe-image")
async def delete_recipe_image(
    file_url: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an image from S3.
    
    This is useful when:
    - User removes an image from a recipe
    - Recipe is deleted (should also delete its image)
    
    Note: In a production app, you might want additional checks like:
    - Verify the file belongs to a recipe the user has access to
    - Soft-delete instead of hard-delete
    
    Args:
        file_url: The full S3 URL of the file to delete
        current_user: The authenticated user
    
    Returns:
        Success message
    
    Raises:
        HTTPException 400: If the URL doesn't match our S3 bucket
        HTTPException 500: If deletion fails
    """
    # Extract the key from the URL
    # URL format: http://localhost:4566/recipe-images/recipes/uuid.jpg
    # or: https://s3.amazonaws.com/bucket-name/recipes/uuid.jpg
    
    try:
        # Get the part after the bucket name
        # This is a simple approach - in production you might want more robust parsing
        if "/recipes/" in file_url:
            # Extract everything from "recipes/" onwards
            key = "recipes/" + file_url.split("/recipes/")[1]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file URL format"
            )
        
        success = delete_file(key)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete file from storage"
            )
        
        return {"message": "File deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing delete request: {str(e)}"
        )

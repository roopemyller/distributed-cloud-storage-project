from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import os

from ...utils import Database
from ...models import User, File
from ..auth.services import require_role, UserResponse, FileResponse

router = APIRouter()
db = Database()

# User management routes
@router.get('/users', response_model=List[UserResponse])
async def list_all_users(
    _current_user = Depends(require_role("admin")),
    db: Session = Depends(db.get_db)
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return users

@router.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    _current_user = Depends(require_role("admin")),
    db: Session = Depends(db.get_db)
):
    """Delete a user (admin only)."""
    # Prevent admins from deleting themselves
    if _current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Delete any files owned by this user
    db.query(File).filter(File.owner_id == str(user_id)).delete()
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    return None

# File management routes
@router.get('/files', response_model=List[FileResponse])
async def list_all_files(
    _current_user = Depends(require_role("admin")),
    db: Session = Depends(db.get_db)
):
    """List all files in the system (admin only)."""
    try:
        # Get all files from the database
        files = db.query(File).all()

        # Get all users for reference
        users = db.query(User).all()

        # Create a dictionary to map user IDs to usernames
        user_dict = {str(user.id): user.username for user in users}

        # Format response with user information
        return [
            FileResponse(
                id=file.id,
                name=file.file_name,
                size=file.size,
                owner_id=file.owner_id,
                owner_username=user_dict.get(str(file.owner_id), "Unknown"),
                timestamp=file.timestamp,
            ) for file in files
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@router.delete('/files/{file_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    _current_user = Depends(require_role("admin")),
    db: Session = Depends(db.get_db)
):
    """Delete a file from the system (admin only)."""
    # Find the file
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File with ID {file_id} not found"
        )
    
    try:
        # Get the file path from the database
        file_path = file.path

        # Delete the physical file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete the file record from database
        db.delete(file)
        db.commit()
        
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )

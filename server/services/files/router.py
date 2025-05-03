# services/file/router.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import os
import uuid

from ...utils import Database
from ...models.models import File
from ..auth.services import get_user_from_token
from .services import (
    FileUploadResponse,
    FileDownload,
    FileListResponse
)


router = APIRouter()
security = HTTPBearer()

@router.post('/upload', response_model=FileUploadResponse)
async def upload(
    file: UploadFile = File(),  
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(Database.get_db)
):
    token = credentials.credentials
    
    try:
        # Get user from token
        user = get_user_from_token(token, db)
        
        # Read file content
        contents = await file.read()
        file_size = len(contents)

        # Create a unique filename with UUID
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"

        # Save file to disk in user-specific folder
        upload_dir = os.path.join("uploads", str(user.id))
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Save file metadata to database
        db_file = File(
            owner_id=str(user.id),
            file_name=file.filename,
            path=file_path,
            size=file_size
        )
        db.add(db_file)
        db.commit()
        
        return {
            "message": f"File uploaded successfully",
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.get('/list', response_model=List[FileListResponse])
async def list_files(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(Database.get_db)
):
    """List all files belonging to the authenticated user"""
    token = credentials.credentials
    
    try:
        # Get user from token
        user = get_user_from_token(token, db)
        
        # Query database for files owned by this user
        files = db.query(File).filter(File.owner_id == str(user.id)).all()
        
        # Format response
        return [
            {
                "id": file.id,
                "name": file.file_name,
                "size": file.size,
                "timestamp": file.timestamp
            } for file in files
        ]
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@router.get('/download')
async def download(
    file_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(Database.get_db)
):
    """Download a file"""
    token = credentials.credentials
    
    try:
        # Get user from token
        user = get_user_from_token(token, db)
        
        # Find the file in database
        file = db.query(File).filter(
            File.owner_id == str(user.id),
            File.file_name == file_name
        ).first()
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return the file
        if os.path.exists(file.path):
            return FileResponse(
                path=file.path,
                filename=file.file_name,
                media_type="application/octet-stream"
            )
        else:
            # File exists in DB but not on disk
            raise HTTPException(status_code=404, detail="File not found on server")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File download failed: {str(e)}")

@router.delete('/{file_id}')
async def delete(
    file_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(Database.get_db)
):
    """Delete a file"""
    token = credentials.credentials
    
    try:
        # Get user from token
        user = get_user_from_token(token, db)
        
        # Find the file in database
        file = db.query(File).filter(
            File.owner_id == str(user.id),
            File.id == file_id
        ).first()
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete the file from disk
        if os.path.exists(file.path):
            os.remove(file.path)
        
        # Delete the file from database
        db.delete(file)
        db.commit()
        
        return {"message": f"File with file_id {file_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File deletion failed: {str(e)}")

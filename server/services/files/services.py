# services/file/services.py
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os
from typing import Dict, Any

from ...config import settings

class FileUploadResponse(BaseModel):
    """Model for file upload response."""
    message: str
    filename: str
    content_type: str
    size: int

class FileDownload(BaseModel):
    """Model for file download response."""
    file_name: str

class FileListResponse(BaseModel):
    """Model for file list response."""
    id: int
    name: str
    size: int
    timestamp: datetime
 

async def upload_file(file: UploadFile, user_data: Dict[str, Any]) -> FileUploadResponse:
    """Upload a file to the server."""
    try:
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        # Make upload directory if it doesn't exist
        upload_dir = settings.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create user-specific directory
        username = user_data.get("sub")
        user_folder = os.path.join(upload_dir, username)
        os.makedirs(user_folder, exist_ok=True)
        
        # Save the file to the user's directory
        file_path = os.path.join(user_folder, file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Return FileUploadResponse
        return FileUploadResponse(
            message="File uploaded successfully",
            filename=file.filename,
            content_type=file.content_type,
            size=file_size
        )
    # Handle exceptions during file upload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

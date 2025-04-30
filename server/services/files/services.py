# services/file/services.py
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel
from datetime import datetime
import os
from typing import Dict, Any

from ...config import settings

class FileUploadResponse(BaseModel):
    message: str
    filename: str
    content_type: str
    size: int

class FileDownload(BaseModel):
    file_name: str

class FileListResponse(BaseModel):
    id: int
    name: str
    size: int
    timestamp: datetime
 

async def upload_file(file: UploadFile, user_data: Dict[str, Any]) -> FileUploadResponse:
    try:
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        upload_dir = settings.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        
        username = user_data.get("sub")
        user_folder = os.path.join(upload_dir, username)
        os.makedirs(user_folder, exist_ok=True)
        
        file_path = os.path.join(user_folder, file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return FileUploadResponse(
            message="File uploaded successfully",
            filename=file.filename,
            content_type=file.content_type,
            size=file_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

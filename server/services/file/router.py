# services/file/router.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

from .services import (
    FileUploadResponse,
    FileDownload
)

router = APIRouter()
security = HTTPBearer()

@router.post('/upload', response_model=FileUploadResponse)
async def upload(
    file: UploadFile = File(...), 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    
    token = credentials.credentials
    print(f"Token received: {token}")
    
    # Process the file
    try:
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        # Save file to disk (optional)
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        return {
            "message": f"File uploaded successfully",
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

# Rest of your routes remain the same

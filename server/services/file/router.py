# services/file/router.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from server.utils import get_token_payload, is_token_expired
from .services import (
    FileUploadResponse,
    upload_file
)

router = APIRouter()
security = HTTPBearer()

@router.post('/upload', response_model=FileUploadResponse)
async def upload(
    file: UploadFile = File(...), 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    if is_token_expired(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
    )

    user_data = get_token_payload(token)
    
    # Process the file using service function
    return await upload_file(file, user_data)
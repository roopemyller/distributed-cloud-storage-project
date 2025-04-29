from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session

from ...utils import Database
from ...config import settings
from ...models import User, File

from .services import (
    authenticate_user, 
    create_access_token, 
    create_user, 
    get_current_user,
    require_role,
    Token, 
    UserCreate, 
    UserResponse,
    FileResponse
)

router = APIRouter()
db = Database()

@router.post('/login', response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db.get_db)):
    """Authenticate a user and return an access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
        user_role=user.role
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/register', response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(db.get_db)):
    """Register a new user."""
    db_user = create_user(db, user)
    return db_user

@router.get('/me', response_model=UserResponse)
async def get_user_me(current_user = Depends(get_current_user)):
    """Get the current authenticated user."""
    return current_user

@router.get('/admin/users', response_model=list[UserResponse])
async def list_all_users(
    _current_user = Depends(require_role("admin")),
    db: Session = Depends(db.get_db)
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return users

@router.get('/admin/files', response_model=list[FileResponse])
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
                size=file.file_size,
                owner_id=file.owner_id,
                owner_username=user_dict.get(str(file.owner_id), "Unknown"),
                timestamp=file.timestamp,
            ) for file in files
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

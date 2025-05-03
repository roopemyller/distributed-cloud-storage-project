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
    # Check if the user exists and verify password
    user = authenticate_user(db, form_data.username, form_data.password)

    # If the user does not exist or password is incorrect, raise an error
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Successfully authenticated, create an access token and return it
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
    try:
        # Check if the user already exists
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        # If not, create the user
        db_user = create_user(db, user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return db_user

@router.get('/me', response_model=UserResponse)
async def get_user_me(current_user = Depends(get_current_user)):
    """Get the current authenticated user."""
    return current_user

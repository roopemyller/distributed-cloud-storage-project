from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from ...models import User
from ...utils import Database, check_token_validity, decode_token
from ...config import settings

db = Database()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

# Helper functions
def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def get_user(db: Session, username: str):
    """Retrieve a user from the database by username."""
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserCreate):
    """Create a new user in the database."""
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    """Authenticate a user by username and password."""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, user_role: str = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # Add role information to the token
    if user_role:
        to_encode.update({"role": user_role})

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(db.get_db)):
    """Get the current user from the token."""
    if not check_token_validity(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = decode_token(token)
    user = get_user(db, username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_user_from_token(token: str, db: Session):
    """Extract user from JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = get_user(db, username=username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Could not validate credentials: {str(e)}")

def require_role(required_role: str):
    """Dependency to check if the user has the required role."""
    def role_checker(token: str = Depends(oauth2_scheme), db: Session = Depends(db.get_db)):
        if not check_token_validity(token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            username: str = payload.get("sub")
            user_role: str = payload.get("role")
            
            if not username or not user_role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token content",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            if user_role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{required_role}' required for this operation",
                )
                
            user = get_user(db, username=username)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
                
            return user
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return role_checker

from datetime import datetime
from typing import Dict, Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from ..config import settings

class TokenData(BaseModel):
    username: Optional[str] = None

def check_token_validity(token: str) -> bool:
    """Check if the token is valid."""
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return True
    except JWTError:
        return False

def decode_token(token: str) -> TokenData:
    """Decode the JWT token and return the payload."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        return TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception

def get_token_payload(token: str) -> Dict:
    """Get the payload from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        raise credentials_exception

def is_token_expired(token: str) -> bool:
    """Check if the token is expired."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp_timestamp = payload.get("exp")
        if exp_timestamp is None:
            # Token is invalid if it has no expiration claim
            return True
        
        # Compare with current timestamp
        current_time = datetime.now().timestamp()
        return current_time > exp_timestamp
    except JWTError:
        # Any decoding error means we treat the token as expired/invalid
        return True

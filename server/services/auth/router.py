# services/auth/router.py
from fastapi import APIRouter

router = APIRouter()

@router.post('/login')
async def login(username: str, password: str):
    return {'message': f'Login attempt for {username}'}

@router.post('/register')
async def register(username: str, password: str, email: str):
    return {'message': f'New user registered: {username}'}
# main.py
from fastapi import FastAPI
from services import auth_router, file_router

app = FastAPI()

app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
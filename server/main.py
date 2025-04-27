# main.py
from fastapi import FastAPI
from server.services.init import auth_router, file_router
from server.models.user import Base
from server.database import engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
app.include_router(file_router, prefix='/files', tags=['Files'])
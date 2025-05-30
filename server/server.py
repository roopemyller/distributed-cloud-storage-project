from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from .services import auth_router, file_router, admin_router
from .utils import Database
from .models.models import Base

db = Database()

@asynccontextmanager
async def lifespan(app):
    # Use SQLAlchemy Base metadata
    Base.metadata.create_all(bind=db.engine)
    yield

# Create app
app = FastAPI(lifespan = lifespan)

# Include routers
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
app.include_router(file_router, prefix='/files', tags=['Files'])
app.include_router(admin_router, prefix='/admin', tags=['Admin'])

@app.get("/")
async def read_root():
    return {"msg": "Hello World"}

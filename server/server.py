from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from .services import auth_router, file_router
from sqlmodel import Session
from .utils import Database

db = Database()

@asynccontextmanager
async def lifespan(app):
    db.create_db_and_tables()
    yield

SessionDep = Annotated[Session, Depends(db.get_session)]

# Create app
app = FastAPI(lifespan = lifespan)
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])
app.include_router(file_router, prefix='/file', tags=['File'])

@app.get("/")
async def read_root():
    return {"msg": "Hello World"}
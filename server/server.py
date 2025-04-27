from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from .services.auth.router import router as auth_router
from sqlmodel import Session
from .utils import init_db, create_db_and_tables, get_session

# Database setup
engine = init_db()

@asynccontextmanager
async def lifespan(app):
    create_db_and_tables(engine)
    yield

SessionDep = Annotated[Session, Depends(get_session)]

# Create app
app = FastAPI(lifespan = lifespan)
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])

@app.get("/")
async def read_root():
    return {"msg": "Hello World"}
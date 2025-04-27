import os
from dotenv import load_dotenv
from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query
from .services import auth_router, file_router
from sqlmodel import Field, Session, SQLModel, create_engine, select
from .models import File, User

# Load env
load_dotenv()

# Database setup
postgres_url = os.getenv("DATABASE_URL")
engine = create_engine(postgres_url, echo=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables(engine)
    yield

def get_session(engine):
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

# Create app
app = FastAPI(lifespan = lifespan)
app.include_router(auth_router, prefix='/auth', tags=['Authentication'])

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)

@app.get("/")
async def read_root():
    return {"msg": "Hello World"}
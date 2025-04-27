# server/utils/database_helpers.py
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

def init_db():
    # Load dotenv
    load_dotenv()

    # Connect DB
    postgres_url = os.getenv("DATABASE_URL")
    engine = create_engine(postgres_url, echo=True)

    # Return engine
    return engine

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)

def get_session(engine):
    with Session(engine) as session:
        yield session
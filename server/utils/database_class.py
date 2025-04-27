# server/utils/database_helpers.py
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker

class Database:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        load_dotenv()

        self.postgres_url = os.getenv("DATABASE_URL")
        self.engine = create_engine(self.postgres_url, echo=True)
        self._initialized = True

    def create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def get_session(self):
        session = Session(self.engine)
        try:
            yield session
        finally:
            session.close()

    def get_db(self):
        """Get a database session."""
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
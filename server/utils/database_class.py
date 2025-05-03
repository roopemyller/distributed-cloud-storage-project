from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from ..config import settings

# Base class for all database models
Base = declarative_base()

class Database:
    """
    Singleton database connection manager.
    
    This class ensures only one database connection is created throughout the application
    and provides methods to get database sessions and create tables.
    """

    # Singleton instance
    _instance = None

    def __new__(cls):
        """Implement singleton pattern by returning existing insta"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the database connection if not already done."""
        if self._initialized:
            return

        self.postgres_url = settings.DATABASE_URL
        self.engine = create_engine(self.postgres_url, echo=True)
        self._initialized = True

    def create_db_and_tables(self):
        """Create all tables defined by the Base metadata."""
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """
        Get a database session as a generator for dependency injection.
        
        Yields:
            Session: A SQLAlchemy session that will be automatically closed
        """
        session = Session(self.engine)
        try:
            yield session
        finally:
            session.close()

    @classmethod
    def get_db(cls):
        """
        Get a database session using SessionLocal factory.
        
        This is an alternative way to get a database session using the sessionmaker.
        
        Yields:
            Session: SQLAlchemy session that will be automatically closed
        """
        instance = cls()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=instance.engine)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

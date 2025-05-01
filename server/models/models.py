from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")

class File(Base):
    __tablename__ = "file"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(String)
    file_name = Column(String, index=True)
    path = Column(String, index=True)
    size = Column(BigInteger)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

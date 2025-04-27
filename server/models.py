from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class User(SQLModel, table=True): 
    id: int | None = Field(default=None, primary_key=True)
    user_name: str = Field(index=True)
    user_password: str = Field(index=True)

class File(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: str
    file_name: str = Field(index=True)
    path: str = Field(index=True)
    size: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "dev"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = "postgresql://user:root@localhost:5432/postgres"
    UPLOAD_FOLDER: str = "./uploads"
    
    class Config:
        env_file = ".env"

settings = Settings()
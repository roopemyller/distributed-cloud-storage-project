class Settings():
    SECRET_KEY = 'heehee'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 Day
    DATABASE_URL = 'postgre'

    class Config():
        env_file = '.env'
settings = Settings()
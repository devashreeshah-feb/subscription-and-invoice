import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SubFlow"
    API_V1_STR: str = "/api/v1"
    
    # Defaults to SQLite if Postgres is unavailable, making it easy to swap later
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./subflow.db")
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey_for_development_only")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    class Config:
        case_sensitive = True

settings = Settings()

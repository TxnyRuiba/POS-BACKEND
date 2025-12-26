from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    # Validación
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

# Uso en security.py
from app.core.config import get_settings

settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
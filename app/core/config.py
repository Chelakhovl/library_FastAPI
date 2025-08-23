# app/core/config.py
from functools import lru_cache

try:
    # Pydantic v2 (рекомендовано)
    from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
    _V2 = True
except ImportError:  # fallback на Pydantic v1
    from pydantic import BaseSettings  # type: ignore
    _V2 = False


if _V2:
    class Settings(BaseSettings):
        # App
        APP_NAME: str = "Book Management System"
        ENV: str = "dev"
        DEBUG: bool = False

        # Database (SQLAlchemy async engine)
        DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/books_db"
        DB_POOL_SIZE: int = 5
        DB_MAX_OVERFLOW: int = 10
        DB_POOL_TIMEOUT: int = 30
        DB_POOL_RECYCLE: int = 1800  # seconds

        # Auth/JWT
        JWT_SECRET: str = "CHANGE_ME"
        JWT_ALG: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

        # Pydantic v2 конфіг (env-файл, ігнор зайвих змінних)
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )
else:
    class Settings(BaseSettings):
        # App
        APP_NAME: str = "Book Management System"
        ENV: str = "dev"
        DEBUG: bool = False

        # Database (SQLAlchemy async engine)
        DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/books_db"
        DB_POOL_SIZE: int = 5
        DB_MAX_OVERFLOW: int = 10
        DB_POOL_TIMEOUT: int = 30
        DB_POOL_RECYCLE: int = 1800  # seconds

        # Auth/JWT
        JWT_SECRET: str = "CHANGE_ME"
        JWT_ALG: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

        # Pydantic v1 конфіг
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Кешований сінглтон для доступу до конфігів у застосунку."""
    return Settings()



settings = get_settings()

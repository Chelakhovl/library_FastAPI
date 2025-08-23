from functools import lru_cache
import os

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
        APP_NAME: str = os.getenv("APP_NAME", "Book Management System")
        ENV: str = os.getenv("ENV", "dev")
        DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

        # Database (SQLAlchemy async engine)
        DATABASE_URL: str = os.getenv("DATABASE_URL")
        DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", 5))
        DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", 10))
        DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", 30))
        DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", 1800))

        # Auth/JWT
        JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME")
        JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

        # Pydantic v2 конфіг
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )
else:
    class Settings(BaseSettings):
        # App
        APP_NAME: str = os.getenv("APP_NAME", "Book Management System")
        ENV: str = os.getenv("ENV", "dev")
        DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

        # Database (SQLAlchemy async engine)
        DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/books_db")
        DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", 5))
        DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", 10))
        DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", 30))
        DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", 1800))

        # Auth/JWT
        JWT_SECRET: str = os.getenv("JWT_SECRET", "CHANGE_ME")
        JWT_ALG: str = os.getenv("JWT_ALG", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, HttpUrl
from pathlib import Path

class Settings(BaseSettings):
    # JWT
    JWT_SECRET_KEY: str = "super_secret_temporary_key_change_in_production"
    JWT_ALGORITHM: str = "HS256"

    # App
    APP_ENV: Literal["development", "staging", "production"] = "development"
    SECRET_KEY: str = "supersecretkey_for_development_only" # Provide default for dev
    
    # Database
    DATABASE_URL: PostgresDsn = "postgresql+asyncpg://postgres:postgres@localhost:5432/soc_copilot" # type: ignore
    DATABASE_POOL_SIZE: int = 10
    
    # External APIs
    QDRANT_URL: str = "http://qdrant:6333"
    
    # MinIO
    MINIO_HOST: str = "minio"
    MINIO_PORT: str = "9000"
    MINIO_ROOT_USER: str = "soc_admin"
    MINIO_ROOT_PASSWORD: str = "soc_admin_password"
    MINIO_SECURE: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "soc-copilot"
    
    # LLM
    OLLAMA_BASE_URL: HttpUrl = "http://localhost:11434" # type: ignore
    LLM_DEFAULT_PROVIDER: str = "omniroute"
    
    # Security
    JWT_PRIVATE_KEY_PATH: Path | None = None
    JWT_PUBLIC_KEY_PATH: Path | None = None
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Pipeline
    MAX_CONCURRENT_INVESTIGATIONS: int = 3
    MAX_FILE_SIZE_MB: int = 100
    TI_CACHE_TTL_SECONDS: int = 3600
    
    # Feature flags
    OFFLINE_MODE: bool = False
    CLAMAV_ENABLED: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

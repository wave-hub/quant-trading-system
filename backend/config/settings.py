"""Application settings using Pydantic."""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    APP_NAME: str = "QuantTradingSystem"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/quant_trading",
        description="PostgreSQL database URL"
    )
    DATABASE_TEST_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/quant_trading_test",
        description="PostgreSQL test database URL"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis URL"
    )
    REDIS_CACHE_URL: str = Field(
        default="redis://localhost:6379/1",
        description="Redis cache URL"
    )

    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/2",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/3",
        description="Celery result backend URL"
    )
    CELERY_TASK_TIME_LIMIT: int = Field(
        default=3600,
        description="Celery task time limit in seconds"
    )
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(
        default=3000,
        description="Celery task soft time limit in seconds"
    )

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )

    # Data Sources
    TUSHARE_TOKEN: str = Field(
        default="",
        description="Tushare API token"
    )
    AKSHARE_ENABLED: bool = Field(
        default=True,
        description="Enable AKShare data source"
    )

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "*"],
        description="CORS allowed origins"
    )

    # Logging
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Log level"
    )
    LOG_FILE: str = Field(
        default="logs/app.log",
        description="Log file path"
    )

    # RQAlpha
    RQALPHA_BUNDLE_PATH: str = Field(
        default="data/bundles",
        description="RQAlpha bundle path"
    )

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = Field(
        default=30,
        description="WebSocket heartbeat interval in seconds"
    )

    # File Upload
    MAX_UPLOAD_SIZE: int = Field(
        default=10485760,  # 10MB
        description="Maximum upload size in bytes"
    )
    UPLOAD_DIR: str = Field(
        default="data/uploads",
        description="Upload directory"
    )

    # Factor Store
    FACTOR_STORE_PATH: str = Field(
        default="data/factors",
        description="Primary factor store path (parquet partitions)",
    )

    @property
    def DATABASE_ASYNC_URL(self) -> str:
        """Get async database URL."""
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def DATABASE_TEST_ASYNC_URL(self) -> str:
        """Get async test database URL."""
        return self.DATABASE_TEST_URL.replace(
            "postgresql://",
            "postgresql+asyncpg://"
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

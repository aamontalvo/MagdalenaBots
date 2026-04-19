"""Configuration management for the water level data processor."""

from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = Field(default="WaterLevelProcessor", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL")
    supabase_key: Optional[str] = Field(default=None, env="SUPABASE_KEY")
    supabase_service_key: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_KEY")
    
    # File paths
    raw_data_path: Path = Field(default=Path("./data/raw"), env="RAW_DATA_PATH")
    processed_data_path: Path = Field(default=Path("./data/processed"), env="PROCESSED_DATA_PATH")
    output_data_path: Path = Field(default=Path("./data/output"), env="OUTPUT_DATA_PATH")
    
    # Processing
    batch_size: int = Field(default=1000, env="BATCH_SIZE")
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    date_format: str = Field(default="%Y-%m-%d", env="DATE_FORMAT")
    timezone: str = Field(default="UTC", env="TIMEZONE")
    data_validation_strict: bool = Field(default=True, env="DATA_VALIDATION_STRICT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
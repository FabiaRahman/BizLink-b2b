from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "BizLink B2B Workflow Automation"
    APP_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///./bizlink.db"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Third-party APIs (optional, for future workflows)
    WHATSAPP_API_TOKEN: str | None = None
    SLACK_WEBHOOK_URL: str | None = None
    GOOGLE_SERVICE_ACCOUNT_KEY: str | None = None

    # Pydantic V2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance - efficient for repeated calls"""
    return Settings()
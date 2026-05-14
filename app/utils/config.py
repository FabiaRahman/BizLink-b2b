import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

# Debug: Print environment info on startup
print(f"🔍 CWD: {os.getcwd()}")
print(f"🔍 .env exists: {os.path.exists('.env')}")
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        content = f.read()
        print(f"🔍 .env has SECRET_KEY: {'SECRET_KEY' in content}")
        if 'SECRET_KEY' in content:
            print(f"🔍 SECRET_KEY preview: {content.split('SECRET_KEY=')[1].split()[0][:20]}...")

class Settings(BaseSettings):
    # ==================== APP ====================
    APP_NAME: str = "BizLink B2B Workflow Automation"
    APP_VERSION: str = "1.0.0"
    
    # ==================== DATABASE ====================
    DATABASE_URL: str = "sqlite:///./bizlink.db"
    
    # ==================== SECURITY ====================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # ==================== GMAIL/SMTP ====================
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # ==================== GOOGLE SHEETS ====================
    GOOGLE_SHEETS_CREDENTIALS_PATH: str = "./config/service_account.json"
    GOOGLE_SHEETS_SPREADSHEET_ID: str = ""
    
    # ==================== SLACK ====================
    SLACK_WEBHOOK_URL: str = ""
    
    # ==================== WHATSAPP (Optional) ====================
    WHATSAPP_API_TOKEN: str | None = None

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
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "MandiSetu - Market Linkages & Price Discovery Platform"
    SECRET_KEY: str = "mandisetu-super-secret-key-change-in-production-sih26132"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "sqlite:///./mandisetu.db"
    AGMARKNET_API_KEY: Optional[str] = ""
    OPEN_METEO_API_URL: str = "https://api.open-meteo.com/v1/forecast"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    BASE_DIR: Path = BASE_DIR
    FRONTEND_DIR: Path = BASE_DIR / "frontend"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

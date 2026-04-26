import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # Tavily Keys
    TAVILY_API_KEY: str = ""
    TAVILY_API_KEY_SECONDARY: str | None = None
    
    # App Config
    APP_NAME: str = "AI Travel Planner"
    DEBUG: bool = False
    
    # LLM Config
    PRIMARY_MODEL: str = "gemini-1.5-flash"
    FALLBACK_MODEL: str = "llama-3.3-70b-versatile"

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env", "../../.env", "../../../.env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
try:
    settings = Settings()
    if not settings.GOOGLE_API_KEY:
        print("[CONFIG-WARNING] GOOGLE_API_KEY is missing from .env")
    if not settings.GROQ_API_KEY:
        print("[CONFIG-WARNING] GROQ_API_KEY is missing from .env")
    print(f"[CONFIG] Loaded. Primary Model: {settings.PRIMARY_MODEL}")
except Exception as e:
    print(f"[CONFIG-ERROR] {e}")
    settings = Settings(_env_file=None)

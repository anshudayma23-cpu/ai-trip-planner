import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str
    GROQ_API_KEY: str
    
    # Tavily Keys (Supporting Fallback)
    TAVILY_API_KEY: str
    TAVILY_API_KEY_SECONDARY: str | None = None
    
    # App Config
    APP_NAME: str = "AI Travel Planner"
    DEBUG: bool = False
    
    # LLM Config
    PRIMARY_MODEL: str = "gemini-2.5-flash"
    FALLBACK_MODEL: str = "llama-3.1-70b-versatile"

    model_config = SettingsConfigDict(
        # Look for .env in current dir and then 3 levels up (root)
        env_file=[".env", "../../../.env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate settings
try:
    settings = Settings()
except Exception as e:
    print(f"Configuration Error: {e}")
    print("Ensure you have created a .env file with the required API keys.")
    # In a real app, we might exit here, but for development we'll let it pass 
    # so the user can see what's missing.
    settings = None

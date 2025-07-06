"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "TODO API"
    version: str = "1.0.0"
    description: str = "A simple TODO API built with FastAPI"
    debug: bool = False
    
    class Config:
        env_file = ".env"


settings = Settings()

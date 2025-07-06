"""
Application configuration settings.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    app_name: str = "TODO API"
    version: str = "1.0.0"
    description: str = "A simple TODO API built with FastAPI"
    debug: bool = False
    
    # Security settings
    ip_allowlist: Optional[str] = None
    secret_key: Optional[str] = None
    
    # Database settings (for future use)
    database_url: Optional[str] = None
    
    # Redis settings (for future use)
    redis_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_ips(self) -> List[str]:
        """Parse IP allowlist into a list of IP addresses."""
        if not self.ip_allowlist:
            return []
        return [ip.strip() for ip in self.ip_allowlist.split(",") if ip.strip()]


settings = Settings()

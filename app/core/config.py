from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60
    ENV: str = "dev"
    
    # Groq AI configuration
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama3-8b-8192"
    
    # CORS configuration
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:4200", 
        "http://localhost:8000",
        "https://localhost:3000",
        "https://localhost:4200",
        "https://praja-frontend.onrender.com"
    ]
    
    # Security settings
    CSRF_PROTECTION_ENABLED: bool = True
    SECURE_COOKIES: bool = True
    
    # Server settings
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        if self.ENV == "prod" or os.getenv("RENDER"):
            render_service_name = os.getenv("RENDER_SERVICE_NAME", "")
            if render_service_name:
                self.ALLOWED_ORIGINS.extend([
                    f"https://{render_service_name}.onrender.com",
                    f"http://{render_service_name}.onrender.com"
                ])
            
            # Add any custom domains
            custom_origins = os.getenv("CUSTOM_ORIGINS", "")
            if custom_origins:
                self.ALLOWED_ORIGINS.extend(custom_origins.split(","))
            
            # Production security settings
            self.SECURE_COOKIES = True
            self.CSRF_PROTECTION_ENABLED = True
        
        # Development settings
        if self.ENV == "dev":
            self.SECURE_COOKIES = False
            # Add any additional dev origins
            self.ALLOWED_ORIGINS.extend([
                "http://127.0.0.1:3000",
                "http://127.0.0.1:4200",
                "http://127.0.0.1:8000"
            ])


settings = Settings()

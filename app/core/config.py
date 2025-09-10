from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 60
    ENV: str = "dev"
    
    ALLOWED_ORIGINS: list = ["http://localhost:4200", "http://localhost:8000"]
    CSRF_PROTECTION_ENABLED: bool = True
    SECURE_COOKIES: bool = True

    class Config:
        env_file = ".env"


settings = Settings()

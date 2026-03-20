from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "GitHub Repo Risk Analyzer API"
    ENVIRONMENT: str = "local"
    LOG_LEVEL: str = "INFO"
    
    # Auth
    JWT_SECRET_KEY: str = "supersecret_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # DB
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/repo_risk"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # GitHub
    GITHUB_TOKEN: str = ""
    
    # Webhooks
    WEBHOOK_SECRET: str = "webhook_secret_change_in_production"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()

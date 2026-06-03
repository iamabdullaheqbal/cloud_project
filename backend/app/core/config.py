from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    MISTRAL_API_KEY: str
    CORS_ORIGINS: str = "http://localhost:3000"
    APP_ENV: str = "development"
    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

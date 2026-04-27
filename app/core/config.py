from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Smart Skill Exchange API"
    environment: str = Field(default="development", alias="ENVIRONMENT")

    supabase_url: str = Field(alias="SUPABASE_URL")
    supabase_key: str = Field(alias="SUPABASE_KEY")
    supabase_jwt_secret: str | None = Field(default=None, alias="SUPABASE_JWT_SECRET")

    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()

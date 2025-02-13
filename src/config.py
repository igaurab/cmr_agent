from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENAI_KEY: str
    OPENCAGE_GEOCODE_API: str
    GOOGLE_MAPS_API_KEY: Optional[str]
    GEMINI_API_KEY: Optional[str]
    OPENAI_MODEL: str = "gpt-4o"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


settings = Settings()

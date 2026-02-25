"""Configuration de l'application."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres de l'application."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = ""
    upload_dir: Path = Path("uploads")
    output_dir: Path = Path("output")


def get_settings() -> Settings:
    return Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = 'Aegis'
    app_version: str = '0.1.0'

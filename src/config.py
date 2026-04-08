from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

class DBParams(EnvSettings):
    url: str = Field(..., alias="DATABASE_URL")

class GeneralParams(EnvSettings):
    environment: str = Field(..., alias="ENVIRONMENT")

class Config(EnvSettings):
    db: DBParams = Field(default_factory=DBParams)
    general: GeneralParams = Field(default_factory=GeneralParams)


def get_config():
    return Config()
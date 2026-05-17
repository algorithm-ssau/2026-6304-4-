from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_PATH = Path(__file__).parent.parent / ".env"

class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH, env_file_encoding="utf-8", extra="allow"
    )

class AiParams(EnvSettings):
    ai_url: str = Field(..., alias="AI_URL")
    model: str = Field(..., alias="MODEL")

class DBParams(EnvSettings):
    url: str = Field(default="sqlite+aiosqlite:///./funpay_bot.db", alias="DATABASE_URL")

class GeneralParams(EnvSettings):
    environment: str = Field(default="dev", alias="ENVIRONMENT")

class TelegramParams(EnvSettings):
    bot_token: str | None = Field(default=None, alias="BOT_TOKEN")

class Config(EnvSettings):
    db: DBParams = Field(default_factory=DBParams)
    general: GeneralParams = Field(default_factory=GeneralParams)
    ai: AiParams = Field(default_factory=AiParams)
    telegram: TelegramParams = Field(default_factory=TelegramParams)

def get_config():
    return Config()
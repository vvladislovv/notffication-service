from dataclasses import dataclass
from environs import Env

@dataclass
class Config:
    bot_token: str
    api_token: str
    DATABASE_URL: str

@dataclass
class Settings:
    config: Config

def get_settings(path: str = None):
    env = Env()
    env.read_env(path)

    return Settings(
        config=Config(
            bot_token=env.str("TOKEN_BOT"),
            api_token=env.str("API_TOKEN"),
            DATABASE_URL=env.str("DATABASE_URL")
        )
    )


settings = get_settings()
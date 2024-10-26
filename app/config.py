from pydantic_settings import BaseSettings, SettingsConfigDict
from httpx import AsyncClient


class Settings(BaseSettings):
    # PostgreSQL settings
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: int

    # FastAPI settings
    FASTAPI_PORT: int
    FRONTEND_PORT: int
    API_ADDRESS: str
    TEAM: str

    @property
    def POSTGRES_URL(self):
        return (f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}')

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
client = AsyncClient()
# формат даты во внешнем API
DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

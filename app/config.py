from pydantic_settings import BaseSettings, SettingsConfigDict
from httpx import AsyncClient, Limits
from redis import ConnectionPool
from celery import Celery


class Settings(BaseSettings):
    # PostgreSQL settings
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    
    # Redis settings
    REDIS_HOST: str
    REDIS_PORT: str

    # FastAPI settings
    FASTAPI_PORT: int
    FRONTEND_PORT: int
    API_ADDRESS: str
    TEAM: str
    TEAM_TOKEN: str
    
    # Notification settings
    MAIL: str
    MAIL_PASSWORD: str

    # JWT settings
    SECRET_KEY: str
    ENCODE_ALGORITHM: str
    
    @property
    def POSTGRES_URL(self):
        return (f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}')

    @property
    def REDIS_URL(self):
        return f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}'

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
client = AsyncClient()
celery_client = Celery("test", broker=settings.REDIS_URL+"/0", backend=settings.REDIS_URL+"/0")
# формат даты во внешнем API
DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'
redis_connection_pool = ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from redis import ConnectionPool

from app.config import settings


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(settings.POSTGRES_URL, echo=False)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
redis_connection_pool = ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


async def get_session() -> AsyncGenerator:
    async with async_session_factory() as session:
        yield session
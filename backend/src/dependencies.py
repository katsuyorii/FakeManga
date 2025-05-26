from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

from .database import async_session
from .redis import redis_client


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session

async def get_redis() -> Redis:
    yield redis_client
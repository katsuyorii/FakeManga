from redis.asyncio import Redis, ConnectionPool

from .config import settings


redis_pool = ConnectionPool(settings.REDIS_URL, max_connections=10)
redis_client = Redis(connection_pool=redis_pool)
from app.db import get_session
from app.caching.redis_cache import RedisCache

from fastapi.security import OAuth2PasswordBearer

from app.instrumentation.tracing import get_tracers

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_db():
    get_session()


async def get_cache() -> RedisCache:
    cache = RedisCache()
    await cache.init_cache()
    try:
        yield cache
    finally:
        await cache.close()

async def get_tracer():
    yield await get_tracers()

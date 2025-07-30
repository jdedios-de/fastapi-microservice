from redis.asyncio import Redis

class RedisCache:
    def __init__(self):
        self.client: Redis | None = None

    async def init_cache(self, redis_url: str = "redis://redis:6379") -> None:
        """Initialize the Redis client."""
        self.client = Redis.from_url(redis_url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        """Get a value from Redis by key."""
        if not self.client:
            raise RuntimeError("Redis client not initialized")
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: int | None = None) -> None:
        """Set a value in Redis with an optional expiration time (seconds)."""
        if not self.client:
            raise RuntimeError("Redis client not initialized")
        await self.client.set(key, value, ex=expire)

    async def close(self) -> None:
        """Close the Redis connection."""
        if self.client:
            await self.client.close()

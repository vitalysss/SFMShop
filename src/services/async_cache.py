import functools
import json

import redis.asyncio as aioredis

redis_client: aioredis.Redis | None = None


def cache_async(ttl: int = 300, prefix: str = "cache"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            if redis_client is None:
                raise RuntimeError("Redis client is not initialized")

            key = f"{prefix}:{func.__name__}:{args}:{kwargs}"

            cached = await redis_client.get(key)

            if cached is not None:
                return json.loads(cached)

            result = await func(*args, **kwargs)

            await redis_client.setex(key, ttl, json.dumps(result, default=str))

            return result

        return wrapper

    return decorator

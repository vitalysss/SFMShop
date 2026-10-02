from contextlib import asynccontextmanager

import asyncpg
import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI

from src.config import PRIMARY_DATABASE_URL, REDIS_URL


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db_pool = await asyncpg.create_pool(
        PRIMARY_DATABASE_URL,
        min_size=1,
        max_size=10,
    )
    app.state.redis = aioredis.from_url(
        REDIS_URL,
        decode_responses=True,
    )
    app.state.http_client = httpx.AsyncClient(timeout=5.0)

    yield

    await app.state.http_client.aclose()
    await app.state.redis.aclose()
    await app.state.db_pool.close()

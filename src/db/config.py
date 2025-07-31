from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.school import models

from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_limiter import FastAPILimiter
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


DATABASE_URL="postgresql+asyncpg://postgres:root@localhost:5432/Practice"

async_engine = create_async_engine(url=DATABASE_URL, echo=True)

Session = sessionmaker(bind=async_engine,class_=AsyncSession, expire_on_commit=False )

async def get_session():
    async with Session() as session:
        yield session

async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def user_identifier(request: Request):
    #This is strictly for throttling. SO, we do not need to query the DB to get the actual user object. We can just get the email directly
    from src.user_auth.utils import decode_token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return "anonymous"
    token = auth_header[len("Bearer "):].strip()
    token_data = decode_token(token)
    user_id = token_data.get('sub','anonymous')
    return user_id


async def init_redis():
    redis = aioredis.from_url("redis://127.0.0.1:6379/1")  # or read from env/config
    FastAPICache.init(RedisBackend(redis), prefix="cache") #not a synchronous function. So, not using await
    db = Annotated[AsyncSession, Depends(get_session)]
    await FastAPILimiter.init(redis, identifier=user_identifier)



from typing import AsyncGenerator, Any
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from loguru import logger

from core.config import settings

metadata = MetaData()
Base = declarative_base(metadata=metadata)
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=30,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def close_db():
    logger.info("Closing database...")
    await engine.dispose()


async def get_db() -> AsyncGenerator[Any, Any]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine

from bot.data.config import DatabaseConfig
from database.models.base import Base
from database.models.users import User
from database.models.receipts import Receipt


def create_engine(database: DatabaseConfig, echo=False):
    engine = create_async_engine(
        database.construct_sqlalchemy_url(),
        query_cache_size=1200,
        pool_size=20,
        max_overflow=200,
        future=True,
        echo=echo,
    )
    return engine


def create_session_pool(engine):
    session_pool = async_sessionmaker(bind=engine, expire_on_commit=False)
    return session_pool


async def run_migrations(engine: AsyncEngine):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    await engine.dispose()

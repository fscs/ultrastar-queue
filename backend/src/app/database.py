from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from .config import settings

async_engine = create_async_engine(settings.DATABASE_URL)


async def init_db() -> None:
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def clean_db() -> None:
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)

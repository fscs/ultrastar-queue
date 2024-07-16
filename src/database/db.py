from sqlmodel import SQLModel
from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker


DATABASE_URL = config("DATABASE_URL")

async_engine = create_async_engine(DATABASE_URL, echo=True)


async def init_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)


async def clean_db():
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.drop_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session

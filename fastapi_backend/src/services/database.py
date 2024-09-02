from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


class DBService:

    def __init__(self, database_url: str):
        self.DATABASE_URL = database_url
        self.async_engine = create_async_engine(self.DATABASE_URL, echo=True)

    async def init_db(self) -> None:
        async with self.async_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

    async def clean_db(self) -> None:
        async with self.async_engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.drop_all)

    async def get_session(self) -> AsyncSession:
        async_session = sessionmaker(bind=self.async_engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            yield session

from typing import List

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import UltrastarSong, User


class DBController:

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


class SessionController:

    @staticmethod
    async def get_songs(session: AsyncSession) -> List[UltrastarSong]:
        statement = select(UltrastarSong)
        result = await session.exec(statement)
        return list(result.fetchall())

    @staticmethod
    async def get_song_by_id(session: AsyncSession, song_id: int) -> UltrastarSong | None:
        song = await session.get(UltrastarSong, song_id)
        return song

    @staticmethod
    async def add_song(session: AsyncSession, song: UltrastarSong) -> UltrastarSong:
        session.add(song)
        await session.commit()
        await session.refresh(song)
        return song

    @staticmethod
    async def get_songs_by_criteria(
            session: AsyncSession,
            title: str | None = None,
            artist: str | None = None,
            ) -> list[UltrastarSong]:

        if title and artist:
            statement = select(UltrastarSong).where(UltrastarSong.title == title, UltrastarSong.artist == artist)
        elif title:
            statement = select(UltrastarSong).where(UltrastarSong.title == title)
        elif artist:
            statement = select(UltrastarSong).where(UltrastarSong.artist == artist)
        else:
            statement = select(UltrastarSong)

        songs = await session.exec(statement)

        return list(songs.all())

    @classmethod
    async def add_song_if_not_in_db(cls, session: AsyncSession, song: UltrastarSong) -> UltrastarSong | None:
        matching_songs = await cls.get_songs_by_criteria(session, title=song.title, artist=song.artist)
        if matching_songs:
            return None
        return await cls.add_song(session, song)

    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
        user = await session.get(User, username)
        return user

    @staticmethod
    async def add_user(session: AsyncSession, user: User) -> User:
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

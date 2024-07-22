from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import UltrastarSong
from typing import List
from sqlmodel import SQLModel
from decouple import config
from sqlalchemy.ext.asyncio import create_async_engine
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


async def get_songs(session: AsyncSession) -> List[UltrastarSong]:
    statement = select(UltrastarSong)
    result = await session.exec(statement)
    return list(result.fetchall())


async def get_song_by_id(session: AsyncSession, song_id: int) -> UltrastarSong | None:
    song = await session.get(UltrastarSong, song_id)
    return song


async def add_song(session: AsyncSession, song: UltrastarSong) -> UltrastarSong:
    session.add(song)
    await session.commit()
    await session.refresh(song)
    return song


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

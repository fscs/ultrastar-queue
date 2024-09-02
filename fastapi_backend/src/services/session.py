from typing import List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.auth import User
from ..models.songs import UltrastarSong


class SessionService:

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
            statement = (select(UltrastarSong)
                         .where(UltrastarSong.title == title, UltrastarSong.artist == artist))
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

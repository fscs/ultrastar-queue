from typing import List

from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession

from .models import UltrastarSong


async def get_songs(session: AsyncSession) -> List[UltrastarSong]:
    statement = select(UltrastarSong).order_by(UltrastarSong.title, UltrastarSong.artist)
    result = await session.exec(statement)
    return list(result.fetchall())


async def get_song_by_id(session: AsyncSession, song_id: int) -> UltrastarSong | None:
    song = await session.get(UltrastarSong, song_id)
    return song


async def get_songs_by_criteria(
        session: AsyncSession,
        title: str | None = None,
        artist: str | None = None,
) -> list[UltrastarSong]:
    if title and artist:
        statement = (select(UltrastarSong)
                     .where(UltrastarSong.title == title, UltrastarSong.artist == artist))
    elif title:
        # statement = select(UltrastarSong).where(UltrastarSong.title == title)
        statement = select(UltrastarSong).where(col(UltrastarSong.title).contains(title))
    elif artist:
        # statement = select(UltrastarSong).where(UltrastarSong.artist == artist)
        statement = select(UltrastarSong).where(col(UltrastarSong.artist).contains(artist))
    else:
        statement = select(UltrastarSong)

    statement = statement.order_by(UltrastarSong.title, UltrastarSong.artist)

    songs = await session.exec(statement)

    return list(songs.all())


async def add_song(session: AsyncSession, song: UltrastarSong) -> UltrastarSong:
    session.add(song)
    await session.commit()
    await session.refresh(song)
    return song


async def add_song_if_not_in_db(session: AsyncSession, song: UltrastarSong) -> UltrastarSong | None:
    matching_songs = await get_songs_by_criteria(session, title=song.title, artist=song.artist)
    if matching_songs:
        return None
    return await add_song(session, song)

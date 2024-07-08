from fastapi import FastAPI, HTTPException, status, Path, Depends
from typing import Annotated
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from database.models import UltrastarSong, UltrastarSongBase
from database.db import init_db, clean_db, get_session


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    clean_db()

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/songs")
async def get_songs(
        session: Session = Depends(get_session)
        ) -> list[UltrastarSong]:
    songs = list(session.exec(select(UltrastarSong)).all())
    if not songs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Songlist is empty")
    return songs


@app.get("/songs/{song_id}")
async def get_song(
        song_id: Annotated[int, Path(title="Id for the Song")],
        session: Session = Depends(get_session)
        ) -> UltrastarSong:
    song = session.get(UltrastarSong, song_id)
    if song is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song_id not found")
    return song


@app.get("/get-songs-by-criteria")
async def get_songs_by_criteria(
        title: str or None = None,
        artist: str or None = None,
        session: Session = Depends(get_session)
        ) -> list[UltrastarSong]:

    songs = []
    # TODO matching für Title in Datenbank und Query
    if title and artist:
        statement = select(UltrastarSong).where(UltrastarSong.title == title, UltrastarSong.artist == artist)
        songs = list(session.exec(statement).all())
    elif title:
        statement = select(UltrastarSong).where(UltrastarSong.title == title)
        songs = list(session.exec(statement).all())
    elif artist:
        statement = select(UltrastarSong).where(UltrastarSong.artist == artist)
        songs = list(session.exec(statement).all())

    if not songs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find songs with provided criteria")
    return songs


@app.post("/create-song/")
async def create_song(
        song_data: UltrastarSongBase,
        session: Session = Depends(get_session)
        ) -> UltrastarSong:
    song = UltrastarSong(title=song_data.title, artist=song_data.artist, lyrics=song_data.lyrics)
    session.add(song)
    session.commit()
    session.refresh(song)
    return song

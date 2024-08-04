from datetime import datetime

from fastapi import APIRouter, status, Response, Depends

from src.auth.controller import is_admin
from src.database.models import UltrastarSong
from src.queue.routes import queue_controller
from src.queue.schemas import SongInQueue

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(is_admin)],
    responses={404: {"description": "Not found"}}
)


@admin_router.post("/add-song", status_code=status.HTTP_201_CREATED, response_model=SongInQueue)
async def add_song_to_queue_as_admin(
        response: Response,
        requested_song: UltrastarSong,
        singer: str):
    song_in_queue = SongInQueue(song=requested_song, singer=singer)
    queue_controller.add_song_at_end(song_in_queue)
    response.set_cookie("last_added", str(datetime.now()), httponly=True)
    return song_in_queue

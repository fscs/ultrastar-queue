from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database.db import init_db, clean_db
from src.queue.routes import queue_router
from src.songs.routes import song_router
from src.auth.routes import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await clean_db()

app = FastAPI(lifespan=lifespan)

app.include_router(queue_router)
app.include_router(song_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

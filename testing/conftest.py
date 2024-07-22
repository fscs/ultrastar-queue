import pytest
from fastapi.testclient import TestClient
from src.app import app
from unittest.mock import MagicMock, patch
from src.database.models import UltrastarSong
from src.songs.schemas import UltrastarSongBase


@pytest.fixture(scope='session')
def client():
    # await init_db()
    yield TestClient(app)
    # await clean_db()


@pytest.fixture()
def song_base1() -> UltrastarSongBase:
    return UltrastarSongBase(title="Fire & Forgive",
                             artist="Powerwolf",
                             lyrics="And we bring fire, sing fire, scream fire and forgive")


@pytest.fixture()
def song_base2() -> UltrastarSongBase:
    return UltrastarSongBase(title="Hardrock Hallelujah",
                             artist="Lordi",
                             lyrics="The saints are crippled on this sinners night lost are the lambs with no guiding "
                                    "light")


@pytest.fixture()
def song1() -> UltrastarSong:
    return UltrastarSong(id=1,
                         title="Fire & Forgive",
                         artist="Powerwolf",
                         lyrics="And we bring fire, sing fire")


@pytest.fixture()
def song2() -> UltrastarSong:
    return UltrastarSong(id=2,
                         title="Hardrock Hallelujah",
                         artist="Lordi",
                         lyrics="The saints are crippled on this sinners night lost are the lambs with no guiding light")


@pytest.fixture()
def mock_db_query_get_songs():
    patcher = patch('src.database.controller.get_songs')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_add_song():
    patcher = patch('src.database.controller.add_song')
    mock = patcher.start()
    yield mock
    patcher.stop()

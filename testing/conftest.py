import pytest
from fastapi.testclient import TestClient
from src.app import app
from unittest.mock import patch
from src.database.models import UltrastarSong
from src.songs.schemas import UltrastarSongBase


@pytest.fixture(scope='session')
def client():
    yield TestClient(app)


@pytest.fixture()
def song1_base() -> UltrastarSongBase:
    return UltrastarSongBase(title="Fire & Forgive",
                             artist="Powerwolf",
                             lyrics="And we bring fire, sing fire, scream fire and forgive")


@pytest.fixture()
def song1() -> UltrastarSong:
    return UltrastarSong(id=1,
                         title="Fire & Forgive",
                         artist="Powerwolf",
                         lyrics="And we bring fire, sing fire, scream fire and forgive")


@pytest.fixture()
def song1_without_id() -> UltrastarSong:
    return UltrastarSong(title="Fire & Forgive",
                         artist="Powerwolf",
                         lyrics="And we bring fire, sing fire, scream fire and forgive")


@pytest.fixture()
def song2_base() -> UltrastarSongBase:
    return UltrastarSongBase(title="Sainted by the Storm",
                             artist="Powerwolf",
                             lyrics="All aboard kissed by the iron fist, we are sainted by the storm Facing the wind")


@pytest.fixture()
def song2() -> UltrastarSong:
    return UltrastarSong(id=2,
                         title="Sainted by the Storm",
                         artist="Powerwolf",
                         lyrics="All aboard kissed by the iron fist, we are sainted by the storm Facing the wind")

"""
@pytest.fixture()
def song2_without_id() -> UltrastarSong:
    return UltrastarSong(title="Sainted by the Storm",
                         artist="Powerwolf",
                         lyrics="All aboard kissed by the iron fist, we are sainted by the storm Facing the wind")
"""

@pytest.fixture()
def mock_db_query_get_songs():
    patcher = patch('src.database.controller.get_songs')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_get_song_by_id():
    patcher = patch('src.database.controller.get_song_by_id')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_add_song():
    patcher = patch('src.database.controller.add_song')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_get_songs_by_criteria():
    patcher = patch('src.database.controller.get_songs_by_criteria')
    mock = patcher.start()
    yield mock
    patcher.stop()

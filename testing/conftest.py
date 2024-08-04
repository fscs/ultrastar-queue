from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.app import db_controller
from src.database.models import UltrastarSong
from src.queue.routes import datetime
from src.queue.schemas import SongInQueue
from src.songs.schemas import UltrastarSongBase


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[db_controller.get_session] = lambda: None
    yield TestClient(app)
    app.dependency_overrides = {}


"""class instances"""


@pytest.fixture()
def song1_base() -> UltrastarSongBase:
    return UltrastarSongBase(title="Fire & Forgive",
                             artist="Powerwolf",
                             lyrics="And we bring fire, sing fire, scream fire and forgive")


@pytest.fixture()
def song2_base() -> UltrastarSongBase:
    return UltrastarSongBase(title="Sainted by the Storm",
                             artist="Powerwolf",
                             lyrics="All aboard kissed by the iron fist, we are sainted by the storm")


@pytest.fixture()
def song1_without_id() -> UltrastarSong:
    return UltrastarSong(title="Fire & Forgive",
                         artist="Powerwolf",
                         lyrics="And we bring fire, sing fire, scream fire and forgive")


@pytest.fixture()
def song1() -> UltrastarSong:
    return UltrastarSong(id=1,
                         title="Fire & Forgive",
                         artist="Powerwolf",
                         lyrics="And we bring fire, sing fire, scream fire and forgive")


@pytest.fixture()
def song2() -> UltrastarSong:
    return UltrastarSong(id=2,
                         title="Sainted by the Storm",
                         artist="Powerwolf",
                         lyrics="All aboard kissed by the iron fist, we are sainted by the storm")


@pytest.fixture()
def song3() -> UltrastarSong:
    return UltrastarSong(id=3,
                         title="Hardrock Hallelujah",
                         artist="Lordi",
                         lyrics="The saints are crippled on this sinners night, "
                                "lost are the lambs with no guiding light")


@pytest.fixture()
def song1_in_queue(song1) -> SongInQueue:
    return SongInQueue(song=song1, singer="Attila")


@pytest.fixture()
def song2_in_queue(song2) -> SongInQueue:
    return SongInQueue(song=song2, singer="Matthew, Charles")


@pytest.fixture()
def song3_in_queue(song3) -> SongInQueue:
    return SongInQueue(song=song3, singer="Mr. Lordi")


"""mock_db"""


@pytest.fixture()
def mock_db_query_get_songs():
    patcher = patch('src.database.controller.SessionController.get_songs')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_get_song_by_id():
    patcher = patch('src.database.controller.SessionController.get_song_by_id')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_add_song():
    patcher = patch('src.database.controller.SessionController.add_song')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_get_songs_by_criteria():
    patcher = patch('src.database.controller.SessionController.get_songs_by_criteria')
    mock = patcher.start()
    yield mock
    patcher.stop()


"""mock_queue_controller"""


@pytest.fixture()
def mock_queue_controller_get_queue():
    patcher = patch('src.queue.controller.QueueController.get_queue')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_queue_controller_add_song_at_end():
    patcher = patch('src.queue.controller.QueueController.add_song_at_end')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_queue_controller_mark_first_song_as_processed():
    patcher = patch('src.queue.controller.QueueController.mark_first_song_as_processed')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_queue_controller_remove_song_by_index():
    patcher = patch('src.queue.controller.QueueController.remove_song_by_index')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_queue_controller_clear_queue():
    patcher = patch('src.queue.controller.QueueController.clear_queue')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def fake_datetime() -> datetime:
    return datetime(year=2021, month=1, day=1, hour=1, minute=1, second=1)


@pytest.fixture()
def mock_queue_routes_datetime(fake_datetime):
    patcher = patch('src.queue.routes.datetime')
    mock = patcher.start()
    yield mock
    patcher.stop()

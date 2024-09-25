from datetime import timedelta, datetime
from typing import Dict, Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from src.app.auth.models import User
from src.app.auth.utils import get_password_hash
from src.app.dependencies import get_async_session
from src.app.main import app
from src.app.queue.schemas import QueueEntry, ProcessedQueueEntry
from src.app.songs.models import UltrastarSong
from src.app.songs.schemas import UltrastarSongBase


@pytest.fixture(scope="session")
def client():
    app.dependency_overrides[get_async_session] = lambda: None
    yield TestClient(app)
    app.dependency_overrides = {}


"""class instances"""


@pytest.fixture()
def song1_base() -> UltrastarSongBase:
    return UltrastarSongBase(title="Fire & Forgive",
                             artist="Powerwolf",
                             audio_duration=timedelta(seconds=270),
                             lyrics="And we bring fire, sing fire, scream fire and forgive")


@pytest.fixture()
def song2_base() -> UltrastarSongBase:
    return UltrastarSongBase(title="Sainted by the Storm",
                             artist="Powerwolf",
                             audio_duration=timedelta(seconds=222),
                             lyrics="All aboard kissed by the iron fist, we are sainted by the storm")


@pytest.fixture()
def song3_base() -> UltrastarSongBase:
    return UltrastarSongBase(title="Hardrock Hallelujah",
                             artist="Lordi",
                             audio_duration=timedelta(seconds=247),
                             lyrics="The saints are crippled on this sinners night, "
                                    "lost are the lambs with no guiding light")


@pytest.fixture()
def song_without_audio_duration_base() -> UltrastarSongBase:
    return UltrastarSongBase(title="Blood Red Sandman",
                             artist="Lordi",
                             audio_duration=None,
                             lyrics="They called me the Leather Apron, they called me Smiling Jack")


@pytest.fixture()
def song1_base_api_wrap(song1_base) -> Dict[str, Any]:
    song1_dict = song1_base.model_dump()
    for key, value in song1_dict.items():
        if type(value) is timedelta:
            song1_dict[key] = value.total_seconds()
    return song1_dict


@pytest.fixture()
def song1_without_id(song1_base) -> UltrastarSong:
    return UltrastarSong(**song1_base.model_dump())


@pytest.fixture()
def song1(song1_base) -> UltrastarSong:
    return UltrastarSong(id=1,
                         **song1_base.model_dump())


@pytest.fixture()
def song2(song2_base) -> UltrastarSong:
    return UltrastarSong(id=2,
                         **song2_base.model_dump())


@pytest.fixture()
def song3(song3_base) -> UltrastarSong:
    return UltrastarSong(id=3,
                         **song3_base.model_dump())


@pytest.fixture()
def song_without_audio_duration(song_without_audio_duration_base) -> UltrastarSong:
    return UltrastarSong(id=4,
                         **song_without_audio_duration_base.model_dump())


@pytest.fixture()
def song1_api_wrap(song1) -> Dict[str, Any]:
    song1_dict = song1.model_dump()
    for key, value in song1_dict.items():
        if type(value) is timedelta:
            song1_dict[key] = value.total_seconds()
    return song1_dict


@pytest.fixture()
def song2_api_wrap(song2) -> Dict[str, Any]:
    song2_dict = song2.model_dump()
    for key, value in song2_dict.items():
        if type(value) is timedelta:
            song2_dict[key] = value.total_seconds()
    return song2_dict


@pytest.fixture()
def song3_api_wrap(song3) -> Dict[str, Any]:
    song3_dict = song3.model_dump()
    for key, value in song3_dict.items():
        if type(value) is timedelta:
            song3_dict[key] = value.total_seconds()
    return song3_dict


@pytest.fixture()
def entry1_in_queue(song1) -> QueueEntry:
    return QueueEntry(song=song1, singer="Attila")


@pytest.fixture()
def entry2_in_queue(song2) -> QueueEntry:
    return QueueEntry(song=song2, singer="Matthew, Charles")


@pytest.fixture()
def entry3_in_queue(song3) -> QueueEntry:
    return QueueEntry(song=song3, singer="Mr. Lordi")


@pytest.fixture()
def entry_without_audio_duration_in_queue(song_without_audio_duration) -> QueueEntry:
    return QueueEntry(song=song_without_audio_duration, singer="singer")


@pytest.fixture()
def entry1_in_queue_api_wrap(song1_api_wrap, entry1_in_queue) -> Dict[str, Any]:
    return {
        "song": song1_api_wrap,
        "singer": entry1_in_queue.singer
    }


@pytest.fixture()
def entry2_in_queue_api_wrap(song2_api_wrap, entry2_in_queue) -> Dict[str, Any]:
    return {
        "song": song2_api_wrap,
        "singer": entry2_in_queue.singer
    }


@pytest.fixture()
def entry3_in_queue_api_wrap(song3_api_wrap, entry3_in_queue) -> Dict[str, Any]:
    return {
        "song": song3_api_wrap,
        "singer": entry3_in_queue.singer
    }


@pytest.fixture()
def entry1_in_processed_queue(entry1_in_queue, fake_datetime) -> ProcessedQueueEntry:
    return ProcessedQueueEntry(song=entry1_in_queue.song, singer=entry1_in_queue.singer, processed_at=fake_datetime)


@pytest.fixture()
def entry2_in_processed_queue(entry2_in_queue, fake_datetime) -> ProcessedQueueEntry:
    return ProcessedQueueEntry(song=entry2_in_queue.song, singer=entry2_in_queue.singer, processed_at=fake_datetime)


@pytest.fixture()
def entry3_in_processed_queue(entry3_in_queue, fake_datetime) -> ProcessedQueueEntry:
    return ProcessedQueueEntry(song=entry3_in_queue.song, singer=entry3_in_queue.singer, processed_at=fake_datetime)


@pytest.fixture()
def entry1_in_processed_queue_api_wrap(entry1_in_queue_api_wrap, fake_datetime) -> Dict[str, Any]:
    wrap = entry1_in_queue_api_wrap.copy()
    wrap.update({"processed_at": str(fake_datetime).replace(" ", "T")})
    return wrap


@pytest.fixture()
def entry2_in_processed_queue_api_wrap(entry2_in_queue_api_wrap, fake_datetime) -> Dict[str, Any]:
    wrap = entry2_in_queue_api_wrap.copy()
    wrap.update({"processed_at": str(fake_datetime).replace(" ", "T")})
    return wrap


@pytest.fixture()
def entry3_in_processed_queue_api_wrap(entry3_in_queue_api_wrap, fake_datetime) -> Dict[str, Any]:
    wrap = entry3_in_queue_api_wrap.copy()
    wrap.update({"processed_at": str(fake_datetime).replace(" ", "T")})
    return wrap


@pytest.fixture()
def admin_password() -> str:
    return "1234"


@pytest.fixture()
def admin(admin_password) -> User:
    return User(username="admin", is_admin=True, hashed_password=get_password_hash(admin_password))


@pytest.fixture()
def token() -> dict[str, str]:
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTYwOTQ4MDg2MX0.QEzAfpnOfOB9"
                        "E87j0WIxs9sQ9RzPTGTz4_o0avz4mKs",
        "token_type": "bearer"}


"""mock_db"""


@pytest.fixture()
def mock_db_query_get_songs():
    patcher = patch('src.app.songs.crud.get_songs')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_get_song_by_id():
    patcher = patch('src.app.songs.crud.get_song_by_id')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_add_song():
    patcher = patch('src.app.songs.crud.add_song')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_get_songs_by_criteria():
    patcher = patch('src.app.songs.crud.get_songs_by_criteria')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_db_query_get_user_by_username():
    patcher = patch('src.app.auth.crud.get_user_by_username')
    mock = patcher.start()
    yield mock
    patcher.stop()


"""mock_queue_service"""


@pytest.fixture()
def fake_datetime() -> datetime:
    return datetime(year=2021, month=1, day=1, hour=1, minute=1, second=1)


@pytest.fixture()
def mock_queue_routes_datetime():
    patcher = patch('src.app.queue.routes.datetime')
    mock = patcher.start()
    yield mock
    patcher.stop()


@pytest.fixture()
def mock_queue_service_datetime():
    patcher = patch('src.app.queue.service.datetime')
    mock = patcher.start()
    yield mock
    patcher.stop()


"""mock auth.utils"""


@pytest.fixture()
def mock_auth_utils_datetime():
    patcher = patch('src.app.auth.utils.datetime')
    mock = patcher.start()
    yield mock
    patcher.stop()


"""mock jwt"""


@pytest.fixture()
def mock_jwt():
    patcher = patch('src.app.dependencies.jwt')
    mock = patcher.start()
    yield mock
    patcher.stop()

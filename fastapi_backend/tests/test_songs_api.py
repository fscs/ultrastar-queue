from fastapi import status

from src.app import app
from src.auth.controller import is_admin
from src.auth.exceptions import NotEnoughPrivilegesHTTPException
from src.songs.exceptions import (
    EmptySonglistHTTPException,
    NoMatchingSongHTTPException,
    SongIdNotMatchingHTTPException)
from .test_main import overrides_is_admin_as_false


def test_get_songs_with_no_song(client, mock_db_query_get_songs):
    mock_db_query_get_songs.return_value = []

    response = client.get("/songs/")

    mock_db_query_get_songs.assert_called_once()
    assert response.status_code == EmptySonglistHTTPException._default_status_code
    assert response.json() == {"detail": EmptySonglistHTTPException._default_detail}


def test_get_songs_with_single_song(client, mock_db_query_get_songs, song1, song1_api_wrap):
    mock_db_query_get_songs.return_value = [song1]

    response = client.get(f"/songs/")

    mock_db_query_get_songs.assert_called_once()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_api_wrap]


def test_get_songs_with_two_songs(client, mock_db_query_get_songs, song1, song1_api_wrap, song2, song2_api_wrap):
    mock_db_query_get_songs.return_value = [song1, song2]

    response = client.get(f"/songs/")

    mock_db_query_get_songs.assert_called_once()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_api_wrap, song2_api_wrap]


def test_get_song_by_id_with_incorrect_id(client, mock_db_query_get_song_by_id, song1):
    mock_db_query_get_song_by_id.return_value = None

    response = client.get(f"/songs/{song1.id}")

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == SongIdNotMatchingHTTPException._default_status_code
    assert response.json() == {"detail": SongIdNotMatchingHTTPException._default_detail}


def test_get_song_by_id_with_correct_id(client, mock_db_query_get_song_by_id, song1, song1_api_wrap):
    mock_db_query_get_song_by_id.return_value = song1

    response = client.get(f"/songs/{song1.id}")

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == song1_api_wrap


def test_get_songs_by_criteria_with_no_criteria(client,
                                                mock_db_query_get_songs_by_criteria,
                                                song1,
                                                song2,
                                                song1_api_wrap,
                                                song2_api_wrap):
    mock_db_query_get_songs_by_criteria.return_value = [song1, song2]

    response = client.get("/songs/get-songs-by-criteria", params={})

    mock_db_query_get_songs_by_criteria.assert_called_once_with(None, None, None)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_api_wrap, song2_api_wrap]


def test_get_songs_by_criteria_with_no_matching_song(client, mock_db_query_get_songs_by_criteria):
    mock_db_query_get_songs_by_criteria.return_value = []

    response = client.get("/songs/get-songs-by-criteria", params={"artist": "Heino"})

    mock_db_query_get_songs_by_criteria.assert_called_once_with(None, None, "Heino")
    assert response.status_code == NoMatchingSongHTTPException._default_status_code
    assert response.json() == {"detail": NoMatchingSongHTTPException._default_detail}


def test_get_songs_by_criteria_with_matching_artist(client,
                                                    mock_db_query_get_songs_by_criteria,
                                                    song1,
                                                    song2,
                                                    song1_api_wrap,
                                                    song2_api_wrap):
    mock_db_query_get_songs_by_criteria.return_value = [song1, song2]

    response = client.get("/songs/get-songs-by-criteria", params={"artist": song1.artist})

    mock_db_query_get_songs_by_criteria.assert_called_once_with(None, None, song1.artist)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_api_wrap, song2_api_wrap]


def test_get_songs_by_criteria_with_matching_title(client, mock_db_query_get_songs_by_criteria, song1, song1_api_wrap):
    mock_db_query_get_songs_by_criteria.return_value = [song1]

    response = client.get("/songs/get-songs-by-criteria", params={"title": song1.title})

    mock_db_query_get_songs_by_criteria.assert_called_once_with(None, song1.title, None)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_api_wrap]


def test_get_songs_by_criteria_with_matching_title_and_artist(client,
                                                              mock_db_query_get_songs_by_criteria,
                                                              song1,
                                                              song1_api_wrap):
    mock_db_query_get_songs_by_criteria.return_value = [song1]

    response = client.get("/songs/get-songs-by-criteria",
                          params={"title": song1.title, "artist": song1.artist})

    mock_db_query_get_songs_by_criteria.assert_called_once_with(None, song1.title, song1.artist)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_api_wrap]


def test_create_song_with_admin_privileges(client,
                                           song1_base,
                                           song1_base_api_wrap,
                                           song1,
                                           song1_without_id,
                                           song1_api_wrap,
                                           mock_db_query_add_song):
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_add_song.return_value = song1

    response = client.post("/songs/create-song", json=song1_base_api_wrap)

    mock_db_query_add_song.assert_called_once_with(session=None, song=song1_without_id)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_api_wrap

    app.dependency_overrides.pop(is_admin)


def test_create_song_with_admin_privileges_and_incomplete_song_data(client,
                                                                    song1_base,
                                                                    song1,
                                                                    song1_without_id,
                                                                    mock_db_query_add_song):
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_add_song.return_value = song1

    response = client.post("/songs/create-song", json={"title": song1.title})

    mock_db_query_add_song.assert_not_called()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    app.dependency_overrides.pop(is_admin)


def test_create_song_without_admin_privileges(client, mock_db_query_add_song, song1_base, song1):
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_add_song.return_value = song1

    response = client.post("/songs/create-song", json=song1_base.model_dump_json())

    mock_db_query_add_song.assert_not_called()
    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}

    app.dependency_overrides.pop(is_admin)

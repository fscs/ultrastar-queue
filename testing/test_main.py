import pytest
from fastapi import HTTPException, status
from src.app import app
from src.database.controller import get_session
from src.auth.controller import is_admin


app.dependency_overrides[get_session] = lambda: None
app.dependency_overrides[is_admin] = lambda: True


def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_get_queue(client):
    response = client.get("/queue/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_songs_with_empty_list(client, mock_db_query_get_songs):
    mock_db_query_get_songs.return_value.method.return_value = []
    with pytest.raises(HTTPException) as exc:
        client.get("/songs/")
    mock_db_query_get_songs.assert_called_once()
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == "Songlist is empty"


# das funktioniert???
"""def test_get_songs_with_empty_list(client, mock_db_query_get_songs):
    mock_db_query_get_songs.return_value.method.return_value = []
    response = client.get("/songs/")
    mock_db_query_get_songs.assert_called_once()
    assert response.status_code == 200
    assert response.json() == []"""


def test_create_song(client, song_base1, song1, mock_db_query_add_song):
    mock_db_query_add_song.return_value.method.return_value = song1
    response = client.post("/songs/create-song", json=song_base1.model_dump())
    mock_db_query_add_song.assert_called_once_with(song_base1)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1.model_dump()


"""def test_create_song(client):
    response = client.post(
        "/songs/create-song",
        json={"title": "ABC", "artist": "DEF", "lyrics": "GHI"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "title": "ABC", "artist": "DEF", "lyrics": "GHI", "id": 1
    }"""


"""@pytest.mark.anyio
async def test_create_song():
    async with AsyncClient(app=app) as ac:
        response = await ac.post("/songs/create-song",
                                 json={"title": "ABC", "artist": "DEF", "lyrics": "GHI"})
    assert response.status_code == 200
    assert response.json() == {
        "title": "ABC", "artist": "DEF", "lyrics": "GHI", "id": "1"
    }
"""
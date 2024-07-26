from fastapi import status
from src.app import app
from src.auth.controller import is_admin
from src.queue.routes import queue_controller
from .test_main import overrides_is_admin_as_false


def _clear_queue_controller():
    queue_controller.clear_queue()
    queue_controller.clear_processed_songs()
    queue_controller.open_queue()


def test_get_empty_queue(client):
    _clear_queue_controller()
    response = client.get("/queue/")

    assert response.status_code == 200
    assert response.json() == []


def test_get_queue_with_one_song(client, song1_in_queue):
    _clear_queue_controller()
    queue_controller.add_song_at_end(song1_in_queue)
    response = client.get("/queue/")

    assert response.status_code == 200
    assert response.json() == [song1_in_queue.model_dump()]

    _clear_queue_controller()


def test_get_queue_with_two_songs(client, song1_in_queue, song2_in_queue):
    _clear_queue_controller()
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.add_song_at_end(song2_in_queue)
    response = client.get("/queue/")

    assert response.status_code == 200
    assert response.json() == [song1_in_queue.model_dump(), song2_in_queue.model_dump()]

    _clear_queue_controller()


def test_add_song_to_queue_with_correct_song_details(client, mock_db_query_get_song_by_id, song1, song1_in_queue):
    _clear_queue_controller()
    mock_db_query_get_song_by_id.return_value = song1
    response = client.post("/queue/add-song", json=song1.model_dump(), params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_controller.get_queue() == [song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue.model_dump()

    _clear_queue_controller()


def test_add_song_to_queue_with_song_not_in_database(client, mock_db_query_get_song_by_id, song1, song1_in_queue):
    _clear_queue_controller()
    mock_db_query_get_song_by_id.return_value = None
    response = client.post("/queue/add-song", json=song1.model_dump(), params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Song not in database"}
    assert queue_controller.get_queue() == []

    _clear_queue_controller()


def test_add_song_to_queue_with_mismatching_song_details(client,
                                                         mock_db_query_get_song_by_id,
                                                         song1, song2, song1_in_queue):
    _clear_queue_controller()
    mock_db_query_get_song_by_id.return_value = song1
    mismatched_song = {"id": song1.id, "title": song2.title, "artist": song2.artist, "lyrics": song2.lyrics}
    response = client.post("/queue/add-song", json=mismatched_song, params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Songdata not matching"}
    assert queue_controller.get_queue() == []

    _clear_queue_controller()


def test_add_song_to_queue_with_closed_queue(client, mock_db_query_get_song_by_id, song1, song1_in_queue):
    _clear_queue_controller()
    queue_controller.close_queue()
    mock_db_query_get_song_by_id.return_value = song1
    response = client.post("/queue/add-song", json=song1.model_dump(), params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Queue is closed. Can't add any more songs."}
    assert queue_controller.get_queue() == []

    _clear_queue_controller()


def test_check_first_song_with_admin_privileges_and_empty_queue(client):
    app.dependency_overrides[is_admin] = lambda: True
    _clear_queue_controller()
    response = client.put("/queue/check-first-song")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Queue is empty"}
    assert queue_controller._processed_songs == []

    _clear_queue_controller()
    app.dependency_overrides.pop(is_admin)


def test_check_first_song_with_admin_privileges_and_one_song_in_queue(client, song1_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clear_queue_controller()
    queue_controller.add_song_at_end(song1_in_queue)
    response = client.put("/queue/check-first-song")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"checked": song1_in_queue.model_dump()}
    assert queue_controller.get_queue() == []
    assert queue_controller._processed_songs == [song1_in_queue]

    _clear_queue_controller()
    app.dependency_overrides.pop(is_admin)


def test_check_first_song_with_admin_privileges_and_two_songs_in_queue(client, song1_in_queue, song2_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clear_queue_controller()
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.add_song_at_end(song2_in_queue)
    response = client.put("/queue/check-first-song")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"checked": song1_in_queue.model_dump()}
    assert queue_controller.get_queue() == [song2_in_queue]
    assert queue_controller._processed_songs == [song1_in_queue]

    _clear_queue_controller()
    app.dependency_overrides.pop(is_admin)


def test_check_first_song_without_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    _clear_queue_controller()
    queue_controller.add_song_at_end(song1_in_queue)
    response = client.put("/queue/check-first-song")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_controller.get_queue() == [song1_in_queue]
    assert queue_controller._processed_songs == []

    _clear_queue_controller()
    app.dependency_overrides.pop(is_admin)


def test_remove_song_from_queue_with_admin_privileges_and_empty_queue(client):
    app.dependency_overrides[is_admin] = lambda: True
    _clear_queue_controller()
    response = client.delete("/queue/remove-song", params={"index": 0})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Requested index is out of bounds"}

    _clear_queue_controller()
    app.dependency_overrides.pop(is_admin)


def test_remove_song_from_queue_with_admin_privileges_and_song_in_queue(client, song1_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clear_queue_controller()
    queue_controller.add_song_at_end(song1_in_queue)
    response = client.delete("/queue/remove-song", params={"index": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"deleted": song1_in_queue.model_dump()}
    assert queue_controller.get_queue() == []

    _clear_queue_controller()
    app.dependency_overrides.pop(is_admin)


def test_remove_song_from_queue_without_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    _clear_queue_controller()
    queue_controller.add_song_at_end(song1_in_queue)
    response = client.delete("/queue/remove-song", params={"index": 0})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_controller.get_queue() == [song1_in_queue]

    _clear_queue_controller()
    app.dependency_overrides.pop(is_admin)


def test_clear_queue_with_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clear_queue_controller()
    queue_controller.add_song_at_end(song1_in_queue)
    response = client.delete("/queue/clear-queue")

    assert response.status_code == 200
    assert response.json() == {"message": "Queue cleared"}
    assert queue_controller.get_queue() == []

    _clear_queue_controller()
    app.dependency_overrides.pop(is_admin)


def test_clear_queue_without_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    _clear_queue_controller()
    queue_controller.add_song_at_end(song1_in_queue)
    response = client.delete("/queue/clear-queue")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_controller.get_queue() == [song1_in_queue]

    _clear_queue_controller()
    app.dependency_overrides.pop(is_admin)

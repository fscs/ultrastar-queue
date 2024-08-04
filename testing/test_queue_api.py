from fastapi import status

from src.app import app
from src.auth.controller import is_admin
from src.auth.exceptions import NotEnoughPrivilegesHTTPException
from src.queue.exceptions import (
    SongNotInDatabaseHTTPException,
    QueueIndexHTTPException,
    QueueEmptyHTTPException,
    QueueClosedHTTPException,
    MismatchingSongDataHTTPException,
    SongAlreadyInQueueHTTPException,
    SongAlreadySungHTTPException,
    CantSubmitSongHTTPException
)
from src.queue.routes import TIME_BETWEEN_SONGS
from src.queue.routes import queue_controller
from .test_main import overrides_is_admin_as_false


def _clean_test_setup(client):
    client.cookies.clear()
    queue_controller.clear_queue_controller()


def test_get_empty_queue(client):
    _clean_test_setup(client)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_queue_with_one_song(client, song1_in_queue):
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_in_queue.model_dump()]

    _clean_test_setup(client)


def test_get_queue_with_two_songs(client, song1_in_queue, song2_in_queue):
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.add_song_at_end(song2_in_queue)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_in_queue.model_dump(), song2_in_queue.model_dump()]

    _clean_test_setup(client)


def test_add_song_to_queue_with_correct_song_details(client, mock_db_query_get_song_by_id, song1, song1_in_queue):
    _clean_test_setup(client)
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-song", json=song1.model_dump(), params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_controller.get_queue() == [song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue.model_dump()

    _clean_test_setup(client)


def test_add_song_to_queue_with_song_not_in_database(client, mock_db_query_get_song_by_id, song1, song1_in_queue):
    _clean_test_setup(client)
    mock_db_query_get_song_by_id.return_value = None

    response = client.post("/queue/add-song", json=song1.model_dump(), params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == SongNotInDatabaseHTTPException._default_status_code
    assert response.json() == {"detail": SongNotInDatabaseHTTPException._default_detail}
    assert queue_controller.get_queue() == []

    _clean_test_setup(client)


def test_add_song_to_queue_with_mismatching_song_details(client,
                                                         mock_db_query_get_song_by_id,
                                                         song1, song2, song1_in_queue):
    _clean_test_setup(client)
    mock_db_query_get_song_by_id.return_value = song1
    mismatched_song = {"id": song1.id, "title": song2.title, "artist": song2.artist, "lyrics": song2.lyrics}

    response = client.post("/queue/add-song", json=mismatched_song, params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == MismatchingSongDataHTTPException._default_status_code
    assert response.json() == {"detail": MismatchingSongDataHTTPException._default_detail}
    assert queue_controller.get_queue() == []

    _clean_test_setup(client)


def test_add_song_to_queue_with_closed_queue(client, mock_db_query_get_song_by_id, song1, song1_in_queue):
    _clean_test_setup(client)
    queue_controller.close_queue()
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-song", json=song1.model_dump(), params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == QueueClosedHTTPException._default_status_code
    assert response.json() == {"detail": QueueClosedHTTPException._default_detail}
    assert queue_controller.get_queue() == []

    _clean_test_setup(client)


def test_add_song_to_queue_with_recently_added_song(client,
                                                    fake_datetime,
                                                    mock_queue_routes_datetime,
                                                    mock_db_query_get_song_by_id,
                                                    song1,
                                                    song1_in_queue
                                                    ):
    _clean_test_setup(client)
    mock_queue_routes_datetime.now.return_value = fake_datetime
    mock_db_query_get_song_by_id.return_value = song1
    client.cookies.update({"last_added": str(fake_datetime)})

    response = client.post("/queue/add-song", json=song1.model_dump(), params={"singer": song1_in_queue.singer})

    mock_queue_routes_datetime.now.assert_called_once()
    assert response.status_code == CantSubmitSongHTTPException._default_status_code
    assert response.json() == {"detail": f"Please wait {TIME_BETWEEN_SONGS} seconds before submitting a new song"}
    assert queue_controller.get_queue() == []

    _clean_test_setup(client)


def test_add_song_to_queue_with_song_already_in_queue(client, song1, song1_in_queue, mock_db_query_get_song_by_id):
    _clean_test_setup(client)
    mock_db_query_get_song_by_id.return_value = song1
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.post("/queue/add-song", json=song1.model_dump(), params={"singer": song1_in_queue.singer})

    assert response.status_code == SongAlreadyInQueueHTTPException._default_status_code
    assert response.json() == {"detail": f"Song {song1} is already in queue"}
    assert queue_controller.get_queue() == [song1_in_queue]

    _clean_test_setup(client)


def test_add_song_to_queue_with_song_aready_sung(client, song1, song1_in_queue, mock_db_query_get_song_by_id):
    _clean_test_setup(client)
    mock_db_query_get_song_by_id.return_value = song1
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.mark_first_song_as_processed()

    response = client.post("/queue/add-song", json=song1.model_dump(), params={"singer": song1_in_queue.singer})

    assert response.status_code == SongAlreadySungHTTPException._default_status_code
    assert response.json() == {"detail": f"Song {song1} has already been sung today"}
    assert queue_controller.get_queue() == []

    _clean_test_setup(client)


def test_check_first_song_with_admin_privileges_and_empty_queue(client):
    app.dependency_overrides[is_admin] = lambda: True
    _clean_test_setup(client)

    response = client.put("/queue/check-first-song")

    assert response.status_code == QueueEmptyHTTPException._default_status_code
    assert response.json() == {"detail": QueueEmptyHTTPException._default_detail}
    assert queue_controller._processed_songs == []

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_check_first_song_with_admin_privileges_and_one_song_in_queue(client, song1, song1_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.put("/queue/check-first-song")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"checked": song1_in_queue.model_dump()}
    assert queue_controller.get_queue() == []
    assert queue_controller._processed_songs == [song1]

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_check_first_song_with_admin_privileges_and_two_songs_in_queue(client, song1, song1_in_queue, song2_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.add_song_at_end(song2_in_queue)

    response = client.put("/queue/check-first-song")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"checked": song1_in_queue.model_dump()}
    assert queue_controller.get_queue() == [song2_in_queue]
    assert queue_controller._processed_songs == [song1]

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_check_first_song_without_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.put("/queue/check-first-song")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.get_queue() == [song1_in_queue]
    assert queue_controller._processed_songs == []

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_remove_song_from_queue_with_admin_privileges_and_empty_queue(client):
    app.dependency_overrides[is_admin] = lambda: True
    _clean_test_setup(client)

    response = client.delete("/queue/remove-song", params={"index": 0})

    assert response.status_code == QueueIndexHTTPException._default_status_code
    assert response.json() == {"detail": QueueIndexHTTPException._default_detail}

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_remove_song_from_queue_with_admin_privileges_and_song_in_queue(client, song1_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/remove-song", params={"index": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"deleted": song1_in_queue.model_dump()}
    assert queue_controller.get_queue() == []

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_remove_song_from_queue_without_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/remove-song", params={"index": 0})

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.get_queue() == [song1_in_queue]

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_clear_queue_with_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/clear-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue cleared"}
    assert queue_controller.get_queue() == []

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_clear_queue_without_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/clear-queue")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.get_queue() == [song1_in_queue]

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_clear_processed_songs_with_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.mark_first_song_as_processed()

    response = client.delete("/queue/clear-processed-songs")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Processed songs cleared"}
    assert queue_controller.get_processed_songs() == []

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_clear_processed_songs_without_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/clear-processed-songs")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.get_queue() == [song1_in_queue]

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_clear_queue_controller_with_admin_privileges(client, song1_in_queue, song2_in_queue):
    app.dependency_overrides[is_admin] = lambda: True
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.add_song_at_end(song2_in_queue)
    queue_controller.mark_first_song_as_processed()
    queue_controller.close_queue()

    response = client.delete("/queue/clear-queue-controller")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue controller cleared"}
    assert queue_controller.get_queue() == []
    assert queue_controller.get_processed_songs() == []
    assert queue_controller.is_queue_open() is True

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)


def test_clear_queue_controller_without_admin_privileges(client, song1_in_queue):
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/clear-queue")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.get_queue() == [song1_in_queue]

    _clean_test_setup(client)
    app.dependency_overrides.pop(is_admin)

from datetime import timedelta

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
    CantSubmitSongHTTPException,
    NotAValidNumberHTTPException
)
from src.queue.routes import TIME_BETWEEN_SUBMITTING_SONGS
from src.queue.routes import queue_controller
from .test_main import overrides_is_admin_as_false


def _clean_test_setup(client):
    client.cookies.clear()
    queue_controller.clear_queue_controller()
    queue_controller.time_between_same_song = timedelta(minutes=60)
    queue_controller.max_times_song_can_be_sung = 2


def test_get_empty_queue(client):
    _clean_test_setup(client)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_queue_with_one_song(client, song1_in_queue, song1_in_queue_api_wrap):
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_in_queue_api_wrap]

    _clean_test_setup(client)


def test_get_queue_with_two_songs(client,
                                  song1_in_queue,
                                  song2_in_queue,
                                  song1_in_queue_api_wrap,
                                  song2_in_queue_api_wrap):
    _clean_test_setup(client)
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.add_song_at_end(song2_in_queue)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_in_queue_api_wrap, song2_in_queue_api_wrap]

    _clean_test_setup(client)


def test_add_song_to_queue_returns_correct_cookie(client,
                                                  mock_db_query_get_song_by_id,
                                                  mock_queue_routes_datetime,
                                                  fake_datetime,
                                                  song1,
                                                  song1_api_wrap,
                                                  song1_in_queue,
                                                  song1_in_queue_api_wrap):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_queue_routes_datetime.now.return_value = fake_datetime
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.cookies.get("last_added").replace('"', '') == str(fake_datetime)

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_with_correct_song_details(client,
                                                     mock_db_query_get_song_by_id,
                                                     song1,
                                                     song1_api_wrap,
                                                     song1_in_queue,
                                                     song1_in_queue_api_wrap):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_controller.queue == [song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_with_song_not_in_database(client,
                                                     mock_db_query_get_song_by_id,
                                                     song1,
                                                     song1_api_wrap,
                                                     song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = None

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == SongNotInDatabaseHTTPException._default_status_code
    assert response.json() == {"detail": SongNotInDatabaseHTTPException._default_detail}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_with_mismatching_song_details(client,
                                                         mock_db_query_get_song_by_id,
                                                         song1,
                                                         song2,
                                                         song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = song1
    mismatched_song = {"id": song1.id, "title": song2.title, "artist": song2.artist, "lyrics": song2.lyrics}

    response = client.post("/queue/add-song", json=mismatched_song, params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == MismatchingSongDataHTTPException._default_status_code
    assert response.json() == {"detail": MismatchingSongDataHTTPException._default_detail}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_with_closed_queue(client,
                                             mock_db_query_get_song_by_id,
                                             song1,
                                             song1_api_wrap,
                                             song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.close_queue()
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == QueueClosedHTTPException._default_status_code
    assert response.json() == {"detail": QueueClosedHTTPException._default_detail}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_with_recently_added_song(client,
                                                    fake_datetime,
                                                    mock_queue_routes_datetime,
                                                    mock_db_query_get_song_by_id,
                                                    song1,
                                                    song1_api_wrap,
                                                    song1_in_queue
                                                    ):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_queue_routes_datetime.now.return_value = fake_datetime
    mock_db_query_get_song_by_id.return_value = song1
    client.cookies.update({"last_added": str(fake_datetime)})

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    mock_queue_routes_datetime.now.assert_called_once()
    assert response.status_code == CantSubmitSongHTTPException._default_status_code
    assert response.json() == {"detail": f"Please wait {TIME_BETWEEN_SUBMITTING_SONGS} before submitting a new song"}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_with_song_added_a_while_ago(client,
                                                       fake_datetime,
                                                       mock_queue_routes_datetime,
                                                       mock_db_query_get_song_by_id,
                                                       song1,
                                                       song1_api_wrap,
                                                       song1_in_queue,
                                                       song1_in_queue_api_wrap
                                                       ):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    client.cookies.update({"last_added": str(fake_datetime)})
    mock_queue_routes_datetime.now.return_value = fake_datetime + timedelta(days=1)
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    mock_queue_routes_datetime.now.assert_called()
    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_controller.queue == [song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_with_song_already_in_queue(client,
                                                      song1,
                                                      song1_api_wrap,
                                                      song1_in_queue,
                                                      mock_db_query_get_song_by_id):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = song1
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.status_code == SongAlreadyInQueueHTTPException._default_status_code
    assert response.json() == {"detail": f"Song {song1.title} by {song1.artist} is already in queue"}
    assert queue_controller.queue == [song1_in_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_with_song_aready_sung_max_times(client,
                                                           song1,
                                                           song1_api_wrap,
                                                           song1_in_queue,
                                                           mock_db_query_get_song_by_id,
                                                           mock_queue_controller_datetime,
                                                           fake_datetime):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_controller_datetime.now.return_value = fake_datetime
    for i in range(0, queue_controller.max_times_song_can_be_sung + 1):
        queue_controller.add_song_at_end(song1_in_queue)
        queue_controller.mark_first_song_as_processed()
    mock_queue_controller_datetime.now.return_value = fake_datetime + timedelta(days=1)

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.status_code == SongAlreadySungHTTPException._default_status_code
    assert response.json() == {"detail": f"Song {song1.title} by {song1.artist} has already been sung a few times "
                                         f"today. Please choose another one."}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_with_song_sung_recently(client,
                                                   song1,
                                                   song1_api_wrap,
                                                   song1_in_queue,
                                                   mock_db_query_get_song_by_id,
                                                   mock_queue_controller_datetime,
                                                   fake_datetime):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_controller_datetime.now.return_value = fake_datetime
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.mark_first_song_as_processed()

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.status_code == SongAlreadySungHTTPException._default_status_code
    assert response.json() == {"detail": f"Song {song1.title} by {song1.artist} has been sung recently. Please choose "
                                         f"another one."}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_check_first_song_with_admin_privileges_and_empty_queue(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/queue/check-first-song")

    assert response.status_code == QueueEmptyHTTPException._default_status_code
    assert response.json() == {"detail": QueueEmptyHTTPException._default_detail}
    assert queue_controller._processed_songs == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_check_first_song_with_admin_privileges_and_one_song_in_queue(client,
                                                                      song1,
                                                                      song1_in_queue,
                                                                      song1_in_queue_api_wrap,
                                                                      song1_in_processed_queue,
                                                                      mock_queue_controller_datetime,
                                                                      fake_datetime):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_queue_controller_datetime.now.return_value = fake_datetime
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.put("/queue/check-first-song")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"checked": song1_in_queue_api_wrap}
    assert queue_controller.queue == []
    assert queue_controller._processed_songs == [song1_in_processed_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_check_first_song_with_admin_privileges_and_two_songs_in_queue(client,
                                                                       song1,
                                                                       song1_in_queue,
                                                                       song1_in_queue_api_wrap,
                                                                       song1_in_processed_queue,
                                                                       song2_in_queue,
                                                                       mock_queue_controller_datetime,
                                                                       fake_datetime):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_queue_controller_datetime.now.return_value = fake_datetime
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.add_song_at_end(song2_in_queue)

    response = client.put("/queue/check-first-song")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"checked": song1_in_queue_api_wrap}
    assert queue_controller.queue == [song2_in_queue]
    assert queue_controller._processed_songs == [song1_in_processed_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_check_first_song_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.put("/queue/check-first-song")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == [song1_in_queue]
    assert queue_controller._processed_songs == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_remove_song_from_queue_with_admin_privileges_and_empty_queue(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.delete("/queue/remove-song", params={"index": 0})

    assert response.status_code == QueueIndexHTTPException._default_status_code
    assert response.json() == {"detail": QueueIndexHTTPException._default_detail}

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_remove_song_from_queue_with_admin_privileges_and_song_in_queue(client,
                                                                        song1_in_queue,
                                                                        song1_in_queue_api_wrap):

    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/remove-song", params={"index": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"deleted": song1_in_queue_api_wrap}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_remove_song_from_queue_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/remove-song", params={"index": 0})

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == [song1_in_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_queue_with_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/clear-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue cleared"}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_queue_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/clear-queue")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == [song1_in_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_processed_songs_with_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.mark_first_song_as_processed()

    response = client.delete("/queue/clear-processed-songs")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Processed songs cleared"}
    assert queue_controller.processed_songs == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_processed_songs_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/clear-processed-songs")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == [song1_in_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_queue_controller_with_admin_privileges(client, song1_in_queue, song2_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.add_song_at_end(song2_in_queue)
    queue_controller.mark_first_song_as_processed()
    queue_controller.close_queue()

    response = client.delete("/queue/clear-queue-controller")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue controller cleared"}
    assert queue_controller.queue == []
    assert queue_controller.processed_songs == []
    assert queue_controller.is_queue_open() is True

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_queue_controller_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.delete("/queue/clear-queue")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == [song1_in_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_as_admin_with_closed_queue(client,
                                                      mock_db_query_get_song_by_id,
                                                      song1,
                                                      song1_api_wrap,
                                                      song1_in_queue,
                                                      song1_in_queue_api_wrap):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_get_song_by_id.return_value = song1
    queue_controller.close_queue()

    response = client.post("/queue/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert queue_controller.queue == [song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_as_admin_with_recently_added_song(client,
                                                             fake_datetime,
                                                             mock_queue_routes_datetime,
                                                             mock_db_query_get_song_by_id,
                                                             song1,
                                                             song1_api_wrap,
                                                             song1_in_queue,
                                                             song1_in_queue_api_wrap):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_queue_routes_datetime.now.return_value = fake_datetime
    mock_db_query_get_song_by_id.return_value = song1
    client.cookies.update({"last_added": str(fake_datetime)})

    response = client.post("/queue/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert queue_controller.queue == [song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_as_admin_with_song_already_in_queue(client,
                                                               song1,
                                                               song1_api_wrap,
                                                               song1_in_queue,
                                                               song1_in_queue_api_wrap,
                                                               mock_db_query_get_song_by_id):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_get_song_by_id.return_value = song1
    queue_controller.add_song_at_end(song1_in_queue)

    response = client.post("/queue/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert queue_controller.queue == [song1_in_queue, song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_as_admin_with_song_aready_sung_max_times(client,
                                                                    song1,
                                                                    song1_api_wrap,
                                                                    song1_in_queue,
                                                                    song1_in_queue_api_wrap,
                                                                    mock_db_query_get_song_by_id,
                                                                    mock_queue_controller_datetime,
                                                                    fake_datetime):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_controller_datetime.now.return_value = fake_datetime
    for i in range(0, queue_controller.max_times_song_can_be_sung + 1):
        queue_controller.add_song_at_end(song1_in_queue)
        queue_controller.mark_first_song_as_processed()
    mock_queue_controller_datetime.now.return_value = fake_datetime + timedelta(days=1)

    response = client.post("/queue/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert queue_controller.queue == [song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_as_admin_with_song_sung_recently(client,
                                                            song1,
                                                            song1_api_wrap,
                                                            song1_in_queue,
                                                            song1_in_queue_api_wrap,
                                                            mock_db_query_get_song_by_id,
                                                            mock_queue_controller_datetime,
                                                            fake_datetime):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_controller_datetime.now.return_value = fake_datetime
    queue_controller.add_song_at_end(song1_in_queue)
    queue_controller.mark_first_song_as_processed()

    response = client.post("/queue/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert queue_controller.queue == [song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_add_song_to_queue_as_admin_without_admin_privileges(client,
                                                             song1,
                                                             song1_api_wrap,
                                                             song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.post("/queue/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_time_between_same_song_to_zero(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/queue/set-time-between-same-song", params={"seconds": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set time to {timedelta(seconds=0)} between submitting the same song"}
    assert queue_controller.time_between_same_song == timedelta(seconds=0)

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_time_between_same_song_to_greater_than_zero(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/queue/set-time-between-same-song", params={"seconds": 120})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set time to {timedelta(seconds=120)} between submitting the same song"}
    assert queue_controller.time_between_same_song == timedelta(seconds=120)

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_time_between_same_song_to_negative_number(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    current_time_between_same_song = queue_controller.time_between_same_song

    response = client.put("/queue/set-time-between-same-song", params={"seconds": -120})

    assert response.status_code == NotAValidNumberHTTPException._default_status_code
    assert response.json() == {"detail": "Time between songs cannot be negative"}
    assert queue_controller.time_between_same_song == current_time_between_same_song

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_time_between_same_song_without_admin_privileges(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    current_time_between_same_song = queue_controller.time_between_same_song

    response = client.put("/queue/set-time-between-same-song", params={"seconds": 120})

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.time_between_same_song == current_time_between_same_song

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_max_times_song_can_be_sung_to_greater_than_zero(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/queue/set-max-times-song-can-be-sung", params={"max_times": 130})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set max times the same song can be sung to {130}"}
    assert queue_controller.max_times_song_can_be_sung == 130

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_max_times_song_can_be_sung_to_zero(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    current_max_times_song_can_be_sung = queue_controller.max_times_song_can_be_sung

    response = client.put("/queue/set-max-times-song-can-be-sung", params={"max_times": 0})

    assert response.status_code == NotAValidNumberHTTPException._default_status_code
    assert response.json() == {"detail": "Number cannot be zero"}
    assert queue_controller.max_times_song_can_be_sung == current_max_times_song_can_be_sung

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_max_times_song_can_be_sung_to_negative_number(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    current_max_times_song_can_be_sung = queue_controller.max_times_song_can_be_sung

    response = client.put("/queue/set-max-times-song-can-be-sung", params={"max_times": -130})

    assert response.status_code == NotAValidNumberHTTPException._default_status_code
    assert response.json() == {"detail": "Number cannot be negative"}
    assert queue_controller.max_times_song_can_be_sung == current_max_times_song_can_be_sung

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_max_times_song_can_be_sung_without_admin_privileges(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    current_max_times_song_can_be_sung = queue_controller.max_times_song_can_be_sung

    response = client.put("/queue/set-max-times-song-can-be-sung", params={"max_times": 130})

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.max_times_song_can_be_sung == current_max_times_song_can_be_sung

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)

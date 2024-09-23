from datetime import timedelta

from fastapi import status

from ....src.api import queue_service
from ....src import app
from backend.src.services.auth import is_admin
from backend.src.api.exceptions.queue import (
    SongNotInDatabaseHTTPException,
    QueueClosedHTTPException,
    SongAlreadyInQueueHTTPException,
    SongAlreadySungHTTPException,
    CantSubmitSongHTTPException
)
from backend.tests.test_main import overrides_is_admin_as_false


def clean_queue_test_setup(client):
    client.cookies.clear()
    queue_service.clear_queue_service()
    queue_service.time_between_same_song = timedelta(minutes=60)
    queue_service.max_times_song_can_be_sung = 2


def test_get_empty_queue(client):
    clean_queue_test_setup(client)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_queue_with_one_song(client, song1_in_queue, song1_in_queue_api_wrap):
    clean_queue_test_setup(client)
    queue_service.add_entry_at_end(song1_in_queue)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_in_queue_api_wrap]

    clean_queue_test_setup(client)


def test_get_queue_with_two_songs(client,
                                  song1_in_queue,
                                  song2_in_queue,
                                  song1_in_queue_api_wrap,
                                  song2_in_queue_api_wrap):
    clean_queue_test_setup(client)
    queue_controller.add_entry_at_end(song1_in_queue)
    queue_controller.add_entry_at_end(song2_in_queue)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_in_queue_api_wrap, song2_in_queue_api_wrap]

    clean_queue_test_setup(client)


def test_add_song_to_queue_returns_correct_cookie(client,
                                                  mock_db_query_get_song_by_id,
                                                  mock_queue_routes_datetime,
                                                  fake_datetime,
                                                  song1,
                                                  song1_api_wrap,
                                                  song1_in_queue,
                                                  song1_in_queue_api_wrap):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_queue_routes_datetime.now.return_value = fake_datetime
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.cookies.get("last_added").replace('"', '') == str(fake_datetime)

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_song_to_queue_with_correct_song_details(client,
                                                     mock_db_query_get_song_by_id,
                                                     song1,
                                                     song1_api_wrap,
                                                     song1_in_queue,
                                                     song1_in_queue_api_wrap):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_controller.queue == [song1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == song1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_song_to_queue_with_song_not_in_database(client,
                                                     mock_db_query_get_song_by_id,
                                                     song1,
                                                     song1_api_wrap,
                                                     song1_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = None

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == SongNotInDatabaseHTTPException._default_status_code
    assert response.json() == {"detail": SongNotInDatabaseHTTPException._default_detail}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_song_to_queue_with_closed_queue(client,
                                             mock_db_query_get_song_by_id,
                                             song1,
                                             song1_api_wrap,
                                             song1_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.queue_is_open = False
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == QueueClosedHTTPException._default_status_code
    assert response.json() == {"detail": QueueClosedHTTPException._default_detail}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_song_to_queue_with_recently_added_song(client,
                                                    fake_datetime,
                                                    mock_queue_routes_datetime,
                                                    mock_db_query_get_song_by_id,
                                                    song1,
                                                    song1_api_wrap,
                                                    song1_in_queue
                                                    ):
    clean_queue_test_setup(client)
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
    clean_queue_test_setup(client)


def test_add_song_to_queue_with_song_added_a_while_ago(client,
                                                       fake_datetime,
                                                       mock_queue_routes_datetime,
                                                       mock_db_query_get_song_by_id,
                                                       song1,
                                                       song1_api_wrap,
                                                       song1_in_queue,
                                                       song1_in_queue_api_wrap
                                                       ):
    clean_queue_test_setup(client)
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
    clean_queue_test_setup(client)


def test_add_song_to_queue_with_song_already_in_queue(client,
                                                      song1,
                                                      song1_api_wrap,
                                                      song1_in_queue,
                                                      mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = song1
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.status_code == SongAlreadyInQueueHTTPException._default_status_code
    assert response.json() == {"detail": f"Song {song1.title} by {song1.artist} is already in queue"}
    assert queue_controller.queue == [song1_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_song_to_queue_with_song_aready_sung_max_times(client,
                                                           song1,
                                                           song1_api_wrap,
                                                           song1_in_queue,
                                                           mock_db_query_get_song_by_id,
                                                           mock_queue_controller_datetime,
                                                           fake_datetime):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_controller_datetime.now.return_value = fake_datetime
    for _ in range(0, queue_controller.max_times_song_can_be_sung + 1):
        queue_controller.add_entry_at_end(song1_in_queue)
        queue_controller.mark_first_entry_as_processed()
    mock_queue_controller_datetime.now.return_value = fake_datetime + timedelta(days=1)

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.status_code == SongAlreadySungHTTPException._default_status_code
    assert response.json() == {"detail": f"Song {song1.title} by {song1.artist} has already been sung a few times "
                                         f"today. Please choose another one."}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_song_to_queue_with_song_sung_recently(client,
                                                   song1,
                                                   song1_api_wrap,
                                                   song1_in_queue,
                                                   mock_db_query_get_song_by_id,
                                                   mock_queue_controller_datetime,
                                                   fake_datetime):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_controller_datetime.now.return_value = fake_datetime
    queue_controller.add_entry_at_end(song1_in_queue)
    queue_controller.mark_first_entry_as_processed()

    response = client.post("/queue/add-song", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.status_code == SongAlreadySungHTTPException._default_status_code
    assert response.json() == {"detail": f"Song {song1.title} by {song1.artist} has been sung recently. Please choose "
                                         f"another one."}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)

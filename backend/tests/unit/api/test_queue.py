from datetime import timedelta

from fastapi import status
from src.app.main import queue_service

from ...test_main import clean_queue_test_setup

"""test /"""


def test_get_queue_with_zero_entries(client):
    clean_queue_test_setup(client)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_queue_with_one_entry(client, entry1_in_queue, entry1_in_queue_api_wrap):
    clean_queue_test_setup(client)
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [entry1_in_queue_api_wrap]

    clean_queue_test_setup(client)


def test_get_queue_with_multiple_entries(client,
                                         entry1_in_queue,
                                         entry2_in_queue,
                                         entry3_in_queue,
                                         entry1_in_queue_api_wrap,
                                         entry2_in_queue_api_wrap,
                                         entry3_in_queue_api_wrap):
    clean_queue_test_setup(client)
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.get("/queue/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [entry1_in_queue_api_wrap, entry2_in_queue_api_wrap, entry3_in_queue_api_wrap]

    clean_queue_test_setup(client)


"""test /processed-entries"""


def test_get_processed_entries_with_zero_entries(client):
    clean_queue_test_setup(client)

    response = client.get("/queue/processed-entries/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_processed_entries_with_one_entry(client,
                                              entry1_in_queue,
                                              entry1_in_processed_queue_api_wrap,
                                              mock_queue_service_datetime,
                                              fake_datetime):
    clean_queue_test_setup(client)
    mock_queue_service_datetime.now.return_value = fake_datetime
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.mark_entry_at_index_as_processed(0)

    response = client.get("/queue/processed-entries/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [entry1_in_processed_queue_api_wrap]

    clean_queue_test_setup(client)


def test_get_processed_entries_with_multiple_entries(client,
                                                     entry1_in_queue,
                                                     entry2_in_queue,
                                                     entry3_in_queue,
                                                     entry1_in_processed_queue_api_wrap,
                                                     entry2_in_processed_queue_api_wrap,
                                                     entry3_in_processed_queue_api_wrap,
                                                     mock_queue_service_datetime,
                                                     fake_datetime):
    clean_queue_test_setup(client)
    mock_queue_service_datetime.now.return_value = fake_datetime
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)
    queue_service.mark_entry_at_index_as_processed(0)
    queue_service.mark_entry_at_index_as_processed(0)
    queue_service.mark_entry_at_index_as_processed(0)

    response = client.get("/queue/processed-entries/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [entry1_in_processed_queue_api_wrap,
                               entry2_in_processed_queue_api_wrap,
                               entry3_in_processed_queue_api_wrap]

    clean_queue_test_setup(client)


"""test /get-time-until-end-of-queue"""


def test_get_time_until_end_of_queue_with_zero_entries(client):
    clean_queue_test_setup(client)

    response = client.get("/queue/get-time-until-end-of-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == 0

    clean_queue_test_setup(client)


def test_get_time_until_end_of_queue_with_one_entry(client, entry1_in_queue):
    clean_queue_test_setup(client)

    response = client.get("/queue/get-time-until-end-of-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == 0

    clean_queue_test_setup(client)


def test_get_time_until_end_of_queue_with_multiple_entries(client,
                                                           entry1_in_queue,
                                                           entry2_in_queue,
                                                           entry3_in_queue):
    clean_queue_test_setup(client)
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.get("/queue/get-time-until-end-of-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == (entry1_in_queue.song.audio_duration +
                               entry2_in_queue.song.audio_duration +
                               entry3_in_queue.song.audio_duration).total_seconds()

    clean_queue_test_setup(client)


def test_get_time_until_end_of_queue_with_multiple_entries_and_processed_entries(client,
                                                                                 entry1_in_queue,
                                                                                 entry2_in_queue,
                                                                                 entry3_in_queue):
    clean_queue_test_setup(client)
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)
    queue_service.mark_entry_at_index_as_processed(0)

    response = client.get("/queue/get-time-until-end-of-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == (entry2_in_queue.song.audio_duration +
                               entry3_in_queue.song.audio_duration).total_seconds()

    clean_queue_test_setup(client)


def test_get_time_until_end_of_queue_with_song_without_audio_duration(client,
                                                                      entry1_in_queue,
                                                                      entry2_in_queue,
                                                                      entry3_in_queue,
                                                                      entry_without_audio_duration_in_queue):
    clean_queue_test_setup(client)
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)
    queue_service.add_entry_at_end(entry_without_audio_duration_in_queue)

    response = client.get("/queue/get-time-until-end-of-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == (entry1_in_queue.song.audio_duration +
                               entry2_in_queue.song.audio_duration +
                               entry3_in_queue.song.audio_duration +
                               timedelta(seconds=0)).total_seconds()

    clean_queue_test_setup(client)


"""test /add-entry"""


def test_add_entry_to_queue_returns_correct_cookie(client,
                                                   song1,
                                                   entry1_in_queue,
                                                   mock_db_query_get_song_by_id,
                                                   mock_queue_routes_datetime,
                                                   fake_datetime):
    clean_queue_test_setup(client)
    mock_queue_routes_datetime.now.return_value = fake_datetime
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-entry",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    assert response.cookies.get("last_added").replace('"', '') == str(fake_datetime)

    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_correct_song_details(client,
                                                      song1,
                                                      entry1_in_queue,
                                                      entry1_in_queue_api_wrap,
                                                      mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-entry",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_service.queue == [entry1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == entry1_in_queue_api_wrap

    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_song_not_in_database(client,
                                                      song1,
                                                      entry1_in_queue,
                                                      mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    mock_db_query_get_song_by_id.return_value = None

    response = client.post("/queue/add-entry",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Requested song cannot be found in the database."}
    assert queue_service.queue == []

    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_closed_queue(client,
                                              song1,
                                              entry1_in_queue,
                                              mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    queue_service.queue_is_open = False
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-entry",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "Queue is closed. Can't add any more songs."}
    assert queue_service.queue == []

    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_recently_added_song(client,
                                                     song1,
                                                     entry1_in_queue,
                                                     fake_datetime,
                                                     mock_queue_routes_datetime,
                                                     mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    mock_queue_routes_datetime.now.return_value = fake_datetime
    mock_db_query_get_song_by_id.return_value = song1
    client.cookies.update({"last_added": str(fake_datetime)})

    response = client.post("/queue/add-entry",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_queue_routes_datetime.now.assert_called_once()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": f"Please wait {queue_service.time_between_song_submissions} before submitting a new song"}
    assert queue_service.queue == []

    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_song_added_a_while_ago(client,
                                                        song1,
                                                        entry1_in_queue,
                                                        entry1_in_queue_api_wrap,
                                                        fake_datetime,
                                                        mock_queue_routes_datetime,
                                                        mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    client.cookies.update({"last_added": str(fake_datetime)})
    mock_queue_routes_datetime.now.return_value = fake_datetime + timedelta(days=1)
    mock_db_query_get_song_by_id.return_value = song1

    response = client.post("/queue/add-entry",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_queue_routes_datetime.now.assert_called()
    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_service.queue == [entry1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == entry1_in_queue_api_wrap

    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_song_already_in_queue(client,
                                                       song1,
                                                       entry1_in_queue,
                                                       mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    mock_db_query_get_song_by_id.return_value = song1
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.post("/queue/add-entry",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": f"Song {song1.title} by {song1.artist} is already in queue"}
    assert queue_service.queue == [entry1_in_queue]

    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_song_aready_sung_max_times(client,
                                                            song1,
                                                            entry1_in_queue,
                                                            mock_db_query_get_song_by_id,
                                                            mock_queue_service_datetime,
                                                            fake_datetime):
    clean_queue_test_setup(client)
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_service_datetime.now.return_value = fake_datetime
    for _ in range(0, queue_service.max_times_song_can_be_sung + 1):
        queue_service.add_entry_at_end(entry1_in_queue)
        queue_service.mark_entry_at_index_as_processed(0)
    mock_queue_service_datetime.now.return_value = fake_datetime + timedelta(days=1)

    response = client.post("/queue/add-entry",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": f"Song {song1.title} by {song1.artist} has already been sung a few times "
                                         f"today. Please choose another one."}
    assert queue_service.queue == []

    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_song_sung_recently(client,
                                                    song1,
                                                    entry1_in_queue,
                                                    mock_db_query_get_song_by_id,
                                                    mock_queue_service_datetime,
                                                    fake_datetime):
    clean_queue_test_setup(client)
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_service_datetime.now.return_value = fake_datetime
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.mark_entry_at_index_as_processed(0)

    response = client.post("/queue/add-entry",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": f"Song {song1.title} by {song1.artist} has been sung recently. Please choose "
                                         f"another one."}
    assert queue_service.queue == []

    clean_queue_test_setup(client)

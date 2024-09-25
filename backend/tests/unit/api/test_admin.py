from datetime import timedelta

from fastapi import status
from src.app.dependencies import is_admin
from src.app.main import app, queue_service
from src.app.queue.config import QueueBaseSettings

from ...test_main import clean_queue_test_setup, overrides_is_admin_as_false

"""test /add-entry-as-admin"""


def test_add_entry_to_queue_with_closed_queue(client,
                                              song1,
                                              entry1_in_queue,
                                              entry1_in_queue_api_wrap,
                                              mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_get_song_by_id.return_value = song1
    queue_service.queue_is_open = False

    response = client.post("/admin/add-entry-as-admin",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_service.queue == [entry1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == entry1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_recently_added_song(client,
                                                     song1,
                                                     entry1_in_queue,
                                                     entry1_in_queue_api_wrap,
                                                     fake_datetime,
                                                     mock_queue_routes_datetime,
                                                     mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_queue_routes_datetime.now.return_value = fake_datetime
    mock_db_query_get_song_by_id.return_value = song1
    client.cookies.update({"last_added": str(fake_datetime)})

    response = client.post("/admin/add-entry-as-admin",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_service.queue == [entry1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == entry1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_song_already_in_queue(client,
                                                       song1,
                                                       entry1_in_queue,
                                                       entry1_in_queue_api_wrap,
                                                       mock_db_query_get_song_by_id):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_get_song_by_id.return_value = song1
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.post("/admin/add-entry-as-admin",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_service.queue == [entry1_in_queue, entry1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == entry1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_song_already_sung_max_times(client,
                                                             song1,
                                                             entry1_in_queue,
                                                             entry1_in_queue_api_wrap,
                                                             mock_db_query_get_song_by_id,
                                                             mock_queue_service_datetime,
                                                             fake_datetime):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_service_datetime.now.return_value = fake_datetime
    for _ in range(0, queue_service.max_times_song_can_be_sung + 1):
        queue_service.add_entry_at_end(entry1_in_queue)
        queue_service.mark_entry_at_index_as_processed(0)
    mock_queue_service_datetime.now.return_value = fake_datetime + timedelta(days=1)

    response = client.post("/admin/add-entry-as-admin",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_service.queue == [entry1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == entry1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_song_sung_recently(client,
                                                    song1,
                                                    entry1_in_queue,
                                                    entry1_in_queue_api_wrap,
                                                    mock_db_query_get_song_by_id,
                                                    mock_queue_service_datetime,
                                                    fake_datetime):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_get_song_by_id.return_value = song1
    mock_queue_service_datetime.now.return_value = fake_datetime
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.mark_entry_at_index_as_processed(0)

    response = client.post("/admin/add-entry-as-admin",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_service.queue == [entry1_in_queue]
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == entry1_in_queue_api_wrap

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_entry_to_queue_with_song_not_in_database(client,
                                                      song1,
                                                      entry1_in_queue,
                                                      entry1_in_queue_api_wrap,
                                                      mock_db_query_get_song_by_id, ):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_db_query_get_song_by_id.return_value = None

    response = client.post("/admin/add-entry-as-admin",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert queue_service.queue == []
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Requested song cannot be found in the database."}

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_add_entry_to_queue_without_admin_privileges(client,
                                                     song1,
                                                     song1_api_wrap,
                                                     entry1_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.post("/admin/add-entry-as-admin",
                           params={"requested_song_id": song1.id, "singer": entry1_in_queue.singer})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.queue == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test mark-entry-at-index-as-processed"""


def test_mark_entry_at_index_as_processed_with_empty_queue(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/mark-entry-at-index-as-processed", params={"index": 0})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Requested index is out of bounds."}
    assert queue_service._processed_entries == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_mark_entry_at_index_as_processed_with_one_entry_in_queue(client,
                                                                  entry1_in_queue,
                                                                  entry1_in_queue_api_wrap,
                                                                  entry1_in_processed_queue,
                                                                  mock_queue_service_datetime,
                                                                  fake_datetime):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_queue_service_datetime.now.return_value = fake_datetime
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.put("/admin/mark-entry-at-index-as-processed", params={"index": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Marked as processed: {entry1_in_queue.song.title} by "
                                          f"{entry1_in_queue.song.artist}"}
    assert queue_service.queue == []
    assert queue_service._processed_entries == [entry1_in_processed_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_mark_entry_at_index_as_processed_with_multiple_entries_in_queue_mark_first_entry(client,
                                                                                          entry1_in_queue,
                                                                                          entry2_in_queue,
                                                                                          entry3_in_queue,
                                                                                          entry1_in_queue_api_wrap,
                                                                                          entry1_in_processed_queue,
                                                                                          mock_queue_service_datetime,
                                                                                          fake_datetime):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_queue_service_datetime.now.return_value = fake_datetime
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.put("/admin/mark-entry-at-index-as-processed", params={"index": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Marked as processed: {entry1_in_queue.song.title} by "
                                          f"{entry1_in_queue.song.artist}"}
    assert queue_service.queue == [entry2_in_queue, entry3_in_queue]
    assert queue_service._processed_entries == [entry1_in_processed_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_mark_entry_at_index_as_processed_marking_third_entry(client,
                                                              entry1_in_queue,
                                                              entry2_in_queue,
                                                              entry3_in_queue,
                                                              entry1_in_queue_api_wrap,
                                                              entry3_in_processed_queue,
                                                              mock_queue_service_datetime,
                                                              fake_datetime):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_queue_service_datetime.now.return_value = fake_datetime
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.put("/admin/mark-entry-at-index-as-processed", params={"index": 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Marked as processed: {entry3_in_queue.song.title} by "
                                          f"{entry3_in_queue.song.artist}"}
    assert queue_service.queue == [entry1_in_queue, entry2_in_queue]
    assert queue_service._processed_entries == [entry3_in_processed_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_mark_entry_at_index_as_processed_without_admin_privileges(client, entry1_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.put("/admin/mark-entry-at-index-as-processed", params={"index": 0})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.queue == [entry1_in_queue]
    assert queue_service._processed_entries == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /remove-entry"""


def test_remove_entry_from_queue_with_empty_queue(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.delete("/admin/remove-entry", params={"index": 0})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Requested index is out of bounds."}

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_remove_entry_from_queue_with_one_song_in_queue(client,
                                                        entry1_in_queue,
                                                        entry1_in_queue_api_wrap):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.delete("/admin/remove-entry", params={"index": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Deleted: {entry1_in_queue.song.title} by {entry1_in_queue.song.artist}"}
    assert queue_service.queue == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_remove_entry_from_queue_with_multiple_songs_in_queue_remove_first_entry(client,
                                                                                 entry1_in_queue,
                                                                                 entry2_in_queue,
                                                                                 entry3_in_queue,
                                                                                 entry1_in_queue_api_wrap):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.delete("/admin/remove-entry", params={"index": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Deleted: {entry1_in_queue.song.title} by {entry1_in_queue.song.artist}"}
    assert queue_service.queue == [entry2_in_queue, entry3_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_remove_entry_from_queue_remove_third_entry(client,
                                                    entry1_in_queue,
                                                    entry2_in_queue,
                                                    entry3_in_queue,
                                                    entry3_in_queue_api_wrap):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.delete("/admin/remove-entry", params={"index": 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Deleted: {entry3_in_queue.song.title} by {entry3_in_queue.song.artist}"}
    assert queue_service.queue == [entry1_in_queue, entry2_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_remove_entry_from_queue_without_admin_privileges(client, entry1_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.delete("/admin/remove-entry", params={"index": 0})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.queue == [entry1_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /move-entry-from-index-to-index"""


def test_move_entry_from_index_to_index_move_entry_to_same_index(client,
                                                                 entry1_in_queue,
                                                                 entry2_in_queue,
                                                                 entry3_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.patch("/admin/move-entry-from-index-to-index", params={"from_index": 1, "to_index": 1})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Moved: {entry2_in_queue.song.title} by {entry2_in_queue.song.artist}"}
    assert queue_service.queue == [entry1_in_queue, entry2_in_queue, entry3_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_move_entry_from_index_to_index_move_entry_to_smaller_index(client,
                                                                    entry1_in_queue,
                                                                    entry2_in_queue,
                                                                    entry3_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.patch("/admin/move-entry-from-index-to-index", params={"from_index": 2, "to_index": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Moved: {entry3_in_queue.song.title} by {entry3_in_queue.song.artist}"}
    assert queue_service.queue == [entry3_in_queue, entry1_in_queue, entry2_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_move_entry_from_index_to_index_move_entry_to_larger_index(client,
                                                                   entry1_in_queue,
                                                                   entry2_in_queue,
                                                                   entry3_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.patch("/admin/move-entry-from-index-to-index", params={"from_index": 0, "to_index": 2})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Moved: {entry1_in_queue.song.title} by {entry1_in_queue.song.artist}"}
    assert queue_service.queue == [entry2_in_queue, entry1_in_queue, entry3_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_move_entry_from_index_to_index_move_entry_to_index_out_of_bounds(client,
                                                                          entry1_in_queue,
                                                                          entry2_in_queue,
                                                                          entry3_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.patch("/admin/move-entry-from-index-to-index", params={"from_index": 1, "to_index": 7})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Moved: {entry2_in_queue.song.title} by {entry2_in_queue.song.artist}"}
    assert queue_service.queue == [entry1_in_queue, entry3_in_queue, entry2_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_move_entry_from_index_to_index_move_entry_from_index_out_of_bounds(client,
                                                                            entry1_in_queue,
                                                                            entry2_in_queue,
                                                                            entry3_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.patch("/admin/move-entry-from-index-to-index", params={"from_index": 7, "to_index": 0})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "The from_index is out of bounds."}
    assert queue_service.queue == [entry1_in_queue, entry2_in_queue, entry3_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /clear-queue"""


def test_clear_queue_with_empty_queue_and_entries_in_processed_queue(client,
                                                                     entry1_in_queue,
                                                                     entry2_in_queue,
                                                                     entry3_in_queue,
                                                                     entry1_in_processed_queue,
                                                                     entry2_in_processed_queue,
                                                                     entry3_in_processed_queue,
                                                                     fake_datetime,
                                                                     mock_queue_service_datetime):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_queue_service_datetime.now.return_value = fake_datetime
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)
    queue_service.mark_entry_at_index_as_processed(0)
    queue_service.mark_entry_at_index_as_processed(0)
    queue_service.mark_entry_at_index_as_processed(0)

    response = client.delete("/admin/clear-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue cleared"}
    assert queue_service.queue == []
    assert queue_service.processed_entries == [entry1_in_processed_queue,
                                               entry2_in_processed_queue,
                                               entry3_in_processed_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_clear_queue_with_entries_in_queue_and_entries_in_processed_queue(client,
                                                                          entry1_in_queue,
                                                                          entry2_in_queue,
                                                                          entry3_in_queue,
                                                                          entry1_in_processed_queue,
                                                                          entry2_in_processed_queue,
                                                                          entry3_in_processed_queue,
                                                                          fake_datetime,
                                                                          mock_queue_service_datetime):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    mock_queue_service_datetime.now.return_value = fake_datetime
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)
    queue_service.mark_entry_at_index_as_processed(0)
    queue_service.mark_entry_at_index_as_processed(0)

    response = client.delete("/admin/clear-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue cleared"}
    assert queue_service.queue == []
    assert queue_service.processed_entries == [entry1_in_processed_queue,
                                               entry1_in_processed_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_clear_queue_without_admin_privileges(client, entry1_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.delete("/admin/clear-queue")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.queue == [entry1_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /clear-processed-entries"""


def test_clear_processed_entries_with_empty_processed_entries(client, entry1_in_queue, entry2_in_queue,
                                                              entry3_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)

    response = client.delete("/admin/clear-processed-entries")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Processed entries cleared"}
    assert queue_service.queue == [entry1_in_queue, entry2_in_queue, entry3_in_queue]
    assert queue_service.processed_entries == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_clear_processed_entries_with_entries(client, entry1_in_queue, entry2_in_queue, entry3_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.add_entry_at_end(entry3_in_queue)
    queue_service.mark_entry_at_index_as_processed(0)
    queue_service.mark_entry_at_index_as_processed(0)

    response = client.delete("/admin/clear-processed-entries")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Processed entries cleared"}
    assert queue_service.queue == [entry3_in_queue]
    assert queue_service.processed_entries == []

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_clear_processed_entries_without_admin_privileges(client, entry1_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.delete("/admin/clear-processed-entries")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.queue == [entry1_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /clear-queue-service"""


def test_clear_queue_service_with_unchanged_service(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.delete("/admin/clear-queue-service")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue Service cleared"}
    assert queue_service.queue == []
    assert queue_service.processed_entries == []
    assert queue_service.queue_is_open == QueueBaseSettings.QUEUE_IS_OPEN

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_clear_queue_service_with_entries_in_service(client, entry1_in_queue, entry2_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_service.add_entry_at_end(entry1_in_queue)
    queue_service.add_entry_at_end(entry2_in_queue)
    queue_service.mark_entry_at_index_as_processed(0)
    queue_service.queue_is_open = not QueueBaseSettings.QUEUE_IS_OPEN

    response = client.delete("/admin/clear-queue-service")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue Service cleared"}
    assert queue_service.queue == []
    assert queue_service.processed_entries == []
    assert queue_service.queue_is_open == QueueBaseSettings.QUEUE_IS_OPEN

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_clear_queue_service_without_admin_privileges(client, entry1_in_queue):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_service.add_entry_at_end(entry1_in_queue)

    response = client.delete("/admin/clear-queue-service")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.queue == [entry1_in_queue]

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /get-time-between-same-song"""


def test_get_time_between_same_song(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.get("/admin/get-time-between-same-song")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == QueueBaseSettings.TIME_BETWEEN_SAME_SONG.total_seconds()

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_get_time_between_same_song_without_admin_privileges(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.get("/admin/get-time-between-same-song")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /set-time-between-same-song"""


def test_set_time_between_same_song_to_zero(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-time-between-same-song", params={"hours": 0, "minutes": 0, "seconds": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set time to {timedelta(seconds=0)} between submitting the same song"}
    assert queue_service.time_between_same_song == timedelta(seconds=0)

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_time_between_same_song_to_greater_than_zero(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-time-between-same-song", params={"hours": 3, "minutes": 4, "seconds": 5})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set time to {timedelta(hours=3, minutes=4, seconds=5)} between submitting "
                                          f"the same song"}
    assert queue_service.time_between_same_song == timedelta(hours=3, minutes=4, seconds=5)

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_time_between_same_song_to_negative_number(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-time-between-same-song", params={"hours": 0, "minutes": 0, "seconds": -120})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Time between songs cannot be negative"}
    assert queue_service.time_between_same_song == QueueBaseSettings.TIME_BETWEEN_SAME_SONG

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_time_between_same_song_without_admin_privileges(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.put("/admin/set-time-between-same-song", params={"hours": 123, "minutes": 234, "seconds": 345})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.time_between_same_song == QueueBaseSettings.TIME_BETWEEN_SAME_SONG

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /get-max-times-song-can-be-sung"""


def test_get_max_times_song_can_be_sung(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.get("/admin/get-max-times-song-can-be-sung")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == QueueBaseSettings.MAX_TIMES_SONG_CAN_BE_SUNG

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_get_max_times_song_can_be_sung_without_admin_privileges(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.get("/admin/get-max-times-song-can-be-sung")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /set-max-times-song-can-be-sung"""


def test_set_max_times_song_can_be_sung_to_greater_than_zero(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-max-times-song-can-be-sung", params={"max_times": 130})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set max times the same song can be sung to {130}"}
    assert queue_service.max_times_song_can_be_sung == 130

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_max_times_song_can_be_sung_to_zero(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-max-times-song-can-be-sung", params={"max_times": 0})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Number cannot be zero"}
    assert queue_service.max_times_song_can_be_sung == QueueBaseSettings.MAX_TIMES_SONG_CAN_BE_SUNG

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_max_times_song_can_be_sung_to_negative_number(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-max-times-song-can-be-sung",
                          params={"max_times": QueueBaseSettings.MAX_TIMES_SONG_CAN_BE_SUNG - 130})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Number cannot be negative"}
    assert queue_service.max_times_song_can_be_sung == QueueBaseSettings.MAX_TIMES_SONG_CAN_BE_SUNG

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_max_times_song_can_be_sung_without_admin_privileges(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.put("/admin/set-max-times-song-can-be-sung",
                          params={"max_times": QueueBaseSettings.MAX_TIMES_SONG_CAN_BE_SUNG + 130})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.max_times_song_can_be_sung == QueueBaseSettings.MAX_TIMES_SONG_CAN_BE_SUNG

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /get-time-between-song-submissions"""


def test_get_time_between_song_submissions(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.get("/admin/get-time-between-song-submissions")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == QueueBaseSettings.TIME_BETWEEN_SONG_SUBMISSIONS.total_seconds()

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_get_time_between_song_submissions_without_admin_privileges(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.get("/admin/get-time-between-song-submissions")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /set-time-between-song-submissions"""


def test_set_time_between_song_submissions_to_zero(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-time-between-song-submissions", params={"hours": 0, "minutes": 0, "seconds": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set time between song submissions to {timedelta(seconds=0)}"}
    assert queue_service.time_between_song_submissions == timedelta(seconds=0)

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_time_between_song_submissions_to_greater_than_zero(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-time-between-song-submissions", params={"hours": 3, "minutes": 4, "seconds": 5})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set time between song submissions to "
                                          f"{timedelta(hours=3, minutes=4, seconds=5)}"}
    assert queue_service.time_between_song_submissions == timedelta(hours=3, minutes=4, seconds=5)

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_time_between_song_submissions_to_negative_number(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-time-between-song-submissions",
                          params={"hours": 0, "minutes": 0, "seconds": -120})

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Time between song submissions cannot be negative"}
    assert queue_service.time_between_song_submissions == QueueBaseSettings.TIME_BETWEEN_SONG_SUBMISSIONS

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_time_between_song_submissions_without_admin_privileges(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.put("/admin/set-time-between-song-submissions",
                          params={"hours": 123, "minutes": 234, "seconds": 345})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.time_between_song_submissions == QueueBaseSettings.TIME_BETWEEN_SONG_SUBMISSIONS

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /get-queue-is-open"""


def test_get_queue_is_open(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.get("/admin/get-queue-is-open")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == QueueBaseSettings.QUEUE_IS_OPEN

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_get_queue_is_open_without_admin_privileges(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.get("/admin/get-queue-is-open")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


"""test /set-queue-is-open"""


def test_set_queue_is_open_with_same_state(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-queue-is-open", params={"open_queue": QueueBaseSettings.QUEUE_IS_OPEN})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set queue is open to {QueueBaseSettings.QUEUE_IS_OPEN}"}
    assert queue_service.queue_is_open == QueueBaseSettings.QUEUE_IS_OPEN

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_queue_is_open_with_changed_state(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-queue-is-open", params={"open_queue": not QueueBaseSettings.QUEUE_IS_OPEN})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set queue is open to {not QueueBaseSettings.QUEUE_IS_OPEN}"}
    assert queue_service.queue_is_open != QueueBaseSettings.QUEUE_IS_OPEN

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)


def test_set_queue_is_open_without_admin_privileges(client):
    clean_queue_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false

    response = client.put("/admin/set-queue-is-open", params={"open_queue": not QueueBaseSettings.QUEUE_IS_OPEN})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not enough privileges"}
    assert queue_service.queue_is_open == QueueBaseSettings.QUEUE_IS_OPEN

    app.dependency_overrides.pop(is_admin)
    clean_queue_test_setup(client)

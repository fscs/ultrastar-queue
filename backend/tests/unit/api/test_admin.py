def test_check_first_song_with_admin_privileges_and_empty_queue(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/queue/check-first-song")

    assert response.status_code == QueueEmptyHTTPException._default_status_code
    assert response.json() == {"detail": QueueEmptyHTTPException._default_detail}
    assert queue_controller._processed_entries == []

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
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.put("/queue/check-first-song")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"checked": song1_in_queue_api_wrap}
    assert queue_controller.queue == []
    assert queue_controller._processed_entries == [song1_in_processed_queue]

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
    queue_controller.add_entry_at_end(song1_in_queue)
    queue_controller.add_entry_at_end(song2_in_queue)

    response = client.put("/admin/check-first-song")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"checked": song1_in_queue_api_wrap}
    assert queue_controller.queue == [song2_in_queue]
    assert queue_controller._processed_entries == [song1_in_processed_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_check_first_song_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.put("/admin/check-first-song")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == [song1_in_queue]
    assert queue_controller._processed_entries == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_remove_song_from_queue_with_admin_privileges_and_empty_queue(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.delete("/admin/remove-song", params={"index": 0})

    assert response.status_code == QueueIndexHTTPException._default_status_code
    assert response.json() == {"detail": QueueIndexHTTPException._default_detail}

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_remove_song_from_queue_with_admin_privileges_and_song_in_queue(client,
                                                                        song1_in_queue,
                                                                        song1_in_queue_api_wrap):

    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.delete("/admin/remove-song", params={"index": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"deleted": song1_in_queue_api_wrap}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_remove_song_from_queue_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.delete("/admin/remove-song", params={"index": 0})

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == [song1_in_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_queue_with_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.delete("/admin/clear-queue")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue cleared"}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_queue_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.delete("/admin/clear-queue")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == [song1_in_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_processed_songs_with_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_controller.add_entry_at_end(song1_in_queue)
    queue_controller.mark_first_entry_as_processed()

    response = client.delete("/admin/clear-processed-songs")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Processed songs cleared"}
    assert queue_controller.processed_entries == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_processed_songs_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.delete("/admin/clear-processed-songs")

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == [song1_in_queue]

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_queue_controller_with_admin_privileges(client, song1_in_queue, song2_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    queue_controller.add_entry_at_end(song1_in_queue)
    queue_controller.add_entry_at_end(song2_in_queue)
    queue_controller.mark_first_entry_as_processed()
    queue_controller.queue_is_open = False

    response = client.delete("/admin/clear-queue-controller")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Queue controller cleared"}
    assert queue_controller.queue == []
    assert queue_controller.processed_entries == []
    assert queue_controller.queue_is_open is True

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_clear_queue_controller_without_admin_privileges(client, song1_in_queue):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.delete("/admin/clear-queue")

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
    queue_controller.queue_is_open = False

    response = client.post("/admin/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

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

    response = client.post("/admin/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

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
    queue_controller.add_entry_at_end(song1_in_queue)

    response = client.post("/admin/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

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
    for _ in range(0, queue_controller.max_times_song_can_be_sung + 1):
        queue_controller.add_entry_at_end(song1_in_queue)
        queue_controller.mark_first_entry_as_processed()
    mock_queue_controller_datetime.now.return_value = fake_datetime + timedelta(days=1)

    response = client.post("/admin/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

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
    queue_controller.add_entry_at_end(song1_in_queue)
    queue_controller.mark_first_entry_as_processed()

    response = client.post("/admin/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

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

    response = client.post("/admin/add-song-as-admin", json=song1_api_wrap, params={"singer": song1_in_queue.singer})

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.queue == []

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_time_between_same_song_to_zero(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-time-between-same-song", params={"seconds": 0})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set time to {timedelta(seconds=0)} between submitting the same song"}
    assert queue_controller.time_between_same_song == timedelta(seconds=0)

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_time_between_same_song_to_greater_than_zero(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-time-between-same-song", params={"seconds": 120})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set time to {timedelta(seconds=120)} between submitting the same song"}
    assert queue_controller.time_between_same_song == timedelta(seconds=120)

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_time_between_same_song_to_negative_number(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    current_time_between_same_song = queue_controller.time_between_same_song

    response = client.put("/admin/set-time-between-same-song", params={"seconds": -120})

    assert response.status_code == NotAValidNumberHTTPException._default_status_code
    assert response.json() == {"detail": "Time between songs cannot be negative"}
    assert queue_controller.time_between_same_song == current_time_between_same_song

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_time_between_same_song_without_admin_privileges(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    current_time_between_same_song = queue_controller.time_between_same_song

    response = client.put("/admin/set-time-between-same-song", params={"seconds": 120})

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.time_between_same_song == current_time_between_same_song

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_max_times_song_can_be_sung_to_greater_than_zero(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True

    response = client.put("/admin/set-max-times-song-can-be-sung", params={"max_times": 130})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Set max times the same song can be sung to {130}"}
    assert queue_controller.max_times_song_can_be_sung == 130

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_max_times_song_can_be_sung_to_zero(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    current_max_times_song_can_be_sung = queue_controller.max_times_song_can_be_sung

    response = client.put("/admin/set-max-times-song-can-be-sung", params={"max_times": 0})

    assert response.status_code == NotAValidNumberHTTPException._default_status_code
    assert response.json() == {"detail": "Number cannot be zero"}
    assert queue_controller.max_times_song_can_be_sung == current_max_times_song_can_be_sung

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_max_times_song_can_be_sung_to_negative_number(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = lambda: True
    current_max_times_song_can_be_sung = queue_controller.max_times_song_can_be_sung

    response = client.put("/admin/set-max-times-song-can-be-sung", params={"max_times": -130})

    assert response.status_code == NotAValidNumberHTTPException._default_status_code
    assert response.json() == {"detail": "Number cannot be negative"}
    assert queue_controller.max_times_song_can_be_sung == current_max_times_song_can_be_sung

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)


def test_set_max_times_song_can_be_sung_without_admin_privileges(client):
    _clean_test_setup(client)
    app.dependency_overrides[is_admin] = overrides_is_admin_as_false
    current_max_times_song_can_be_sung = queue_controller.max_times_song_can_be_sung

    response = client.put("/admin/set-max-times-song-can-be-sung", params={"max_times": 130})

    assert response.status_code == NotEnoughPrivilegesHTTPException._default_status_code
    assert response.json() == {"detail": NotEnoughPrivilegesHTTPException._default_detail}
    assert queue_controller.max_times_song_can_be_sung == current_max_times_song_can_be_sung

    app.dependency_overrides.pop(is_admin)
    _clean_test_setup(client)
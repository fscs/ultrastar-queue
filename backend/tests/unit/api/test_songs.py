from fastapi import status

"""test /"""


def test_get_songs_with_no_song(client, mock_db_query_get_songs):
    mock_db_query_get_songs.return_value = []

    response = client.get("/songs/")

    mock_db_query_get_songs.assert_called_once()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Songlist is empty"}


def test_get_songs_with_single_song(client, mock_db_query_get_songs, song1, song1_api_wrap):
    mock_db_query_get_songs.return_value = [song1]

    response = client.get("/songs/")

    mock_db_query_get_songs.assert_called_once()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_api_wrap]


def test_get_songs_with_multiple_songs(client,
                                       mock_db_query_get_songs,
                                       song1,
                                       song2,
                                       song3,
                                       song1_api_wrap,
                                       song2_api_wrap,
                                       song3_api_wrap):
    mock_db_query_get_songs.return_value = [song1, song2, song3]

    response = client.get("/songs/")

    mock_db_query_get_songs.assert_called_once()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_api_wrap, song2_api_wrap, song3_api_wrap]


"""test /{song_id}"""


def test_get_song_by_id_with_incorrect_id(client, mock_db_query_get_song_by_id, song1):
    mock_db_query_get_song_by_id.return_value = None

    response = client.get(f"/songs/{song1.id}")

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Requested song id cannot be found in database"}


def test_get_song_by_id_with_correct_id(client, mock_db_query_get_song_by_id, song1, song1_api_wrap):
    mock_db_query_get_song_by_id.return_value = song1

    response = client.get(f"/songs/{song1.id}")

    mock_db_query_get_song_by_id.assert_called_once_with(None, song1.id)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == song1_api_wrap


"""test /get-songs-by-criteria"""


def test_get_songs_by_criteria_with_no_criteria(client,
                                                mock_db_query_get_songs_by_criteria,
                                                song1,
                                                song2,
                                                song1_api_wrap,
                                                song2_api_wrap):
    mock_db_query_get_songs_by_criteria.return_value = [song1, song2]

    response = client.get("songs/get-songs-by-criteria", params={})

    mock_db_query_get_songs_by_criteria.assert_called_once_with(None, None, None)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [song1_api_wrap, song2_api_wrap]


def test_get_songs_by_criteria_with_no_matching_song(client, mock_db_query_get_songs_by_criteria):
    mock_db_query_get_songs_by_criteria.return_value = []

    response = client.get("/songs/get-songs-by-criteria", params={"artist": "Heino"})

    mock_db_query_get_songs_by_criteria.assert_called_once_with(None, None, "Heino")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Could not find songs with provided criteria"}


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

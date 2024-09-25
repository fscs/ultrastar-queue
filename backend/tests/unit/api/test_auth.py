from fastapi import status
from jwt.exceptions import InvalidTokenError

from ...test_main import clean_queue_test_setup

"""test /token"""


def test_get_token_with_correct_credentials(client,
                                            admin,
                                            admin_password,
                                            mock_db_query_get_user_by_username,
                                            mock_auth_utils_datetime,
                                            fake_datetime,
                                            token):
    clean_queue_test_setup(client)
    mock_db_query_get_user_by_username.return_value = admin
    mock_auth_utils_datetime.now.return_value = fake_datetime

    response = client.post("/auth/token", data={"username": admin.username, "password": admin_password})

    mock_db_query_get_user_by_username.assert_called_with(None, admin.username)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == token

    clean_queue_test_setup(client)


def test_get_token_with_incorrect_userame(client,
                                          admin,
                                          admin_password,
                                          mock_db_query_get_user_by_username,
                                          mock_auth_utils_datetime,
                                          fake_datetime):
    clean_queue_test_setup(client)
    mock_db_query_get_user_by_username.return_value = None
    mock_auth_utils_datetime.now.return_value = fake_datetime

    response = client.post("/auth/token", data={"username": admin.username + "!", "password": admin_password})

    mock_db_query_get_user_by_username.assert_called_with(None, admin.username + "!")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


def test_get_token_with_incorrect_password(client,
                                           admin,
                                           admin_password,
                                           mock_db_query_get_user_by_username,
                                           mock_auth_utils_datetime,
                                           fake_datetime):
    clean_queue_test_setup(client)
    mock_db_query_get_user_by_username.return_value = admin
    mock_auth_utils_datetime.now.return_value = fake_datetime

    response = client.post("/auth/token", data={"username": admin.username, "password": admin_password + "!"})

    mock_db_query_get_user_by_username.assert_called_with(None, admin.username)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


def test_get_token_with_incorrect_username_and_password(client,
                                                        admin,
                                                        admin_password,
                                                        mock_db_query_get_user_by_username,
                                                        mock_auth_utils_datetime,
                                                        fake_datetime):
    clean_queue_test_setup(client)
    mock_db_query_get_user_by_username.return_value = None
    mock_auth_utils_datetime.now.return_value = fake_datetime

    response = client.post("/auth/token", data={"username": admin.username + "!", "password": admin_password + "!"})

    mock_db_query_get_user_by_username.assert_called_with(None, admin.username + "!")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


"""test /login"""


def test_login_with_correct_credentials(client,
                                        admin,
                                        admin_password,
                                        mock_db_query_get_user_by_username,
                                        mock_auth_utils_datetime,
                                        fake_datetime,
                                        token):
    clean_queue_test_setup(client)
    mock_db_query_get_user_by_username.return_value = admin
    mock_auth_utils_datetime.now.return_value = fake_datetime

    response = client.post("/auth/login", data={"username": admin.username, "password": admin_password})

    mock_db_query_get_user_by_username.assert_called_with(None, admin.username)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"user": True,
                               "username": admin.username,
                               "is_admin": True,
                               "message": "Successfully logged in!"}
    assert response.cookies.get("access_token").replace('"', '') == token["access_token"]

    clean_queue_test_setup(client)


def test_login_with_incorrect_userame(client,
                                      admin,
                                      admin_password,
                                      mock_db_query_get_user_by_username,
                                      mock_auth_utils_datetime,
                                      fake_datetime):
    clean_queue_test_setup(client)
    mock_db_query_get_user_by_username.return_value = None
    mock_auth_utils_datetime.now.return_value = fake_datetime

    response = client.post("/auth/login", data={"username": admin.username + "!", "password": admin_password})

    mock_db_query_get_user_by_username.assert_called_with(None, admin.username + "!")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


def test_login_with_incorrect_password(client,
                                       admin,
                                       admin_password,
                                       mock_db_query_get_user_by_username,
                                       mock_auth_utils_datetime,
                                       fake_datetime):
    clean_queue_test_setup(client)
    mock_db_query_get_user_by_username.return_value = admin
    mock_auth_utils_datetime.now.return_value = fake_datetime

    response = client.post("/auth/login", data={"username": admin.username, "password": admin_password + "!"})

    mock_db_query_get_user_by_username.assert_called_with(None, admin.username)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


def test_login_with_incorrect_username_and_password(client,
                                                    admin,
                                                    admin_password,
                                                    mock_db_query_get_user_by_username,
                                                    mock_auth_utils_datetime,
                                                    fake_datetime):
    clean_queue_test_setup(client)
    mock_db_query_get_user_by_username.return_value = None
    mock_auth_utils_datetime.now.return_value = fake_datetime

    response = client.post("/auth/login", data={"username": admin.username + "!", "password": admin_password + "!"})

    mock_db_query_get_user_by_username.assert_called_with(None, admin.username + "!")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


"""test /logout"""


def test_logout_while_logged_in(client,
                                admin,
                                mock_db_query_get_user_by_username,
                                mock_jwt,
                                token):
    clean_queue_test_setup(client)
    client.cookies.update({"access_token": token["access_token"]})
    mock_db_query_get_user_by_username.return_value = admin
    mock_jwt.decode.return_value = {"sub": admin.username}

    response = client.post("/auth/logout")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Successfully logged out!"}
    assert response.cookies.get("access_token") is None

    clean_queue_test_setup(client)


def test_logout_while_not_logged_in(client,
                                    admin,
                                    admin_password):
    clean_queue_test_setup(client)

    response = client.post("/auth/logout", data={"username": admin.username, "password": admin_password})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


"""test /current-user"""


def test_get_current_user_with_valid_token(client,
                                           admin,
                                           admin_password,
                                           mock_db_query_get_user_by_username,
                                           mock_auth_utils_datetime,
                                           mock_jwt,
                                           fake_datetime,
                                           token):
    clean_queue_test_setup(client)
    client.cookies.update({"access_token": token["access_token"]})
    mock_db_query_get_user_by_username.return_value = admin
    mock_jwt.decode.return_value = {"sub": admin.username}

    response = client.post("/auth/current-user")

    assert response.status_code == status.HTTP_200_OK

    clean_queue_test_setup(client)


def test_get_current_user_without_token(client):
    clean_queue_test_setup(client)

    response = client.post("/auth/current-user")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


def test_get_current_user_with_invalid_token(client,
                                             admin,
                                             admin_password,
                                             mock_db_query_get_user_by_username,
                                             mock_auth_utils_datetime,
                                             mock_jwt,
                                             fake_datetime,
                                             token):
    clean_queue_test_setup(client)
    client.cookies.update({"access_token": token["access_token"]})
    mock_db_query_get_user_by_username.return_value = admin
    mock_jwt.decode.side_effect = InvalidTokenError

    response = client.post("/auth/current-user")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


def test_get_current_user_with_invalid_username(client,
                                                admin,
                                                admin_password,
                                                mock_db_query_get_user_by_username,
                                                mock_auth_utils_datetime,
                                                mock_jwt,
                                                fake_datetime,
                                                token):
    clean_queue_test_setup(client)
    client.cookies.update({"access_token": token["access_token"]})
    mock_jwt.decode.return_value = {"sub": ""}
    mock_db_query_get_user_by_username.return_value = None

    response = client.post("/auth/current-user")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)


def test_get_current_user_with_no_username(client,
                                           admin,
                                           admin_password,
                                           mock_db_query_get_user_by_username,
                                           mock_auth_utils_datetime,
                                           mock_jwt,
                                           fake_datetime,
                                           token):
    clean_queue_test_setup(client)
    client.cookies.update({"access_token": token["access_token"]})
    mock_jwt.decode.return_value = {}
    mock_db_query_get_user_by_username.return_value = None

    response = client.post("/auth/current-user")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}
    assert response.headers["WWW-Authenticate"] == "Bearer"

    clean_queue_test_setup(client)

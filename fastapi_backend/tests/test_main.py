from fastapi import status, HTTPException


def overrides_is_admin_as_false():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough privileges")


def test_get_main(client):
    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}

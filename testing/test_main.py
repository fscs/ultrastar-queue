from fastapi import status, HTTPException
from src.app import app
from src.database.controller import get_session
from src.auth.controller import is_admin


app.dependency_overrides[get_session] = lambda: None


def overrides_is_admin_as_false():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough privileges")


def test_get_main(client):
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Hello World"}

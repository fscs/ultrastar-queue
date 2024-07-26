from fastapi import Depends, APIRouter
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from .schemas import Token, UserBase
from src.fake import fake_users
from src.database.models import User
from .controller import authenticate_user, create_access_token, get_current_user
from .exceptions import AuthenticationHTTPException

auth_router = APIRouter(
    # prefix="/auth",
    tags=["auth"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)


@auth_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate_user(fake_users, form_data.username, form_data.password)
    if not user:
        raise AuthenticationHTTPException()
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/users/me", response_model=UserBase)
async def read_users_me(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

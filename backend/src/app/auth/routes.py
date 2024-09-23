from fastapi import Depends, APIRouter, Header, Response, status

from .crud import authenticate_user
from .dependencies import OAuth2PasswordRequestFormDep
from .exceptions import AuthenticationHTTPException
from .schemas import Token
from .utils import create_access_token
from ..dependencies import get_current_user, AsyncSessionDep, CurrentUserDep

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)


@auth_router.post("/token")
async def token(session: AsyncSessionDep,
                form_data: OAuth2PasswordRequestFormDep,
                headers: str | None = Header(None)
                ) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise AuthenticationHTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Incorrect username or password",
                                          headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@auth_router.post("/login")
async def login(session: AsyncSessionDep,
                form_data: OAuth2PasswordRequestFormDep,
                response: Response,
                headers: str | None = Header(None),
                ):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise AuthenticationHTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Incorrect username or password",
                                          headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(data={"sub": user.username})
    response.set_cookie("access_token", access_token, httponly=True, max_age=60 * 24)
    return {"user": True, "username": user.username, "is_admin": user.is_admin, "message": "Successfully logged in!"}


@auth_router.post("/logout", dependencies=[Depends(get_current_user)])
async def logout(response: Response,
                 headers: str | None = Header(None)
                 ):
    response.set_cookie("access_token", "", httponly=True, max_age=0)

    return {"message": "Successfully logged out!"}


@auth_router.post("/current-user")
async def get_current_user(user: CurrentUserDep,
                           response: Response,
                           headers: str | None = Header(None)
                           ):
    if not user:
        return {"user": False, "detail": "User does not exist"}
    return {"user": True, "username": user.username, "is_admin": user.is_admin}

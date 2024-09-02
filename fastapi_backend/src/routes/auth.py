from typing import Annotated

from fastapi import Depends, APIRouter, Header, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from ..app import db_controller
from ..exceptions.auth import AuthenticationHTTPException
from ..schemas.auth import Token
from ..services import auth

auth_router = APIRouter(
    # prefix="/auth",
    tags=["auth"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)


@auth_router.post("/token")
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                headers: str | None = Header(None),
                session: AsyncSession = Depends(db_controller.get_session)) -> Token:
    user = await auth.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise AuthenticationHTTPException()
    access_token = auth.create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")


@auth_router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                response: Response,
                headers: str | None = Header(None),
                session: AsyncSession = Depends(db_controller.get_session)):
    user = await auth.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise AuthenticationHTTPException()
    access_token = auth.create_access_token(data={"sub": user.username})
    response.set_cookie("access_token", access_token, httponly=True, max_age=60 * 24)
    return {"user": True, "username": user.username, "is_admin": user.is_admin, "message": "Successfully logged in!"}


@auth_router.post("/logout", dependencies=[Depends(auth.get_current_user)])
async def logout(response: Response,
                 headers: str | None = Header(None)):
    response.set_cookie("access_token", "", httponly=True, max_age=0)

    return {"message": "Successfully logged out!"}


@auth_router.post("/current-user")
async def get_current_user(response: Response,
                           headers: str | None = Header(None),
                           user: Depends = Depends(auth.get_current_user)):
    if not user:
        return {"user": False, "detail": "User not existent"}
    return {"user": True, "username": user.username, "is_admin": user.is_admin}

from typing import Annotated

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app import db_controller
from .controller import authenticate_user, create_access_token
from .exceptions import AuthenticationHTTPException
from .schemas import Token

auth_router = APIRouter(
    # prefix="/auth",
    tags=["auth"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)


@auth_router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: AsyncSession = Depends(db_controller.get_session)) -> Token:
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise AuthenticationHTTPException()
    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")

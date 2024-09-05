from typing import Annotated

import jwt
from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from .auth.crud import get_user_by_username
from .auth.exceptions import CredentialsHTTPException, NotEnoughPrivilegesHTTPException
from .auth.models import User
from .auth.schemas import TokenData
from .config import settings
from .database import async_engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_async_session() -> AsyncSession:
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_current_user(  # token: TokenDep,
        session: AsyncSessionDep,
        access_token: str | None = Cookie(None)) -> User:
    token = access_token
    try:
        payload = jwt.decode(token, settings.JWT_SIGNING_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsHTTPException()
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise CredentialsHTTPException()
    user = await get_user_by_username(session, username=token_data.username)
    if user is None:
        raise CredentialsHTTPException()
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def is_admin(user: CurrentUserDep) -> User:
    if not user.is_admin:
        raise NotEnoughPrivilegesHTTPException()
    return user


AdminDep = Annotated[User, Depends(is_admin)]

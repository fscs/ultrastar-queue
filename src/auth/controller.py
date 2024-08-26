from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from decouple import config
from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app import db_controller
from src.database import SessionController
from src.database.models import User
from .exceptions import CredentialsHTTPException, NotEnoughPrivilegesHTTPException
from .schemas import TokenData

JWT_SIGNING_SECRET_KEY = config("JWT_SIGNING_SECRET_KEY")
JWT_ALGORITHM = config("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(session: AsyncSession, username: str) -> User | None:
    user = await SessionController.get_user_by_username(session, username)
    return user


async def get_current_user(#token: Annotated[str, Depends(oauth2_scheme)],
                           session: Annotated[AsyncSession, Depends(db_controller.get_session)],
                           access_token: str | None = Cookie(None)) -> User:
    token = access_token
    try:
        payload = jwt.decode(token, JWT_SIGNING_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsHTTPException()
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise CredentialsHTTPException()
    user = await get_user(session, username=token_data.username)
    if user is None:
        raise CredentialsHTTPException()
    return user


async def is_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_admin:
        raise NotEnoughPrivilegesHTTPException()
    return user


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
    user = await get_user(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SIGNING_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

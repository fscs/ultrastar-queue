from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Annotated
from passlib.context import CryptContext
from database.models import User
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from decouple import config

SECRET_KEY = config("SECRET_KEY")
JWT_ALGORITHM = config("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users = {
    "bestUser": {"username": "bestUser",
                 "hashed_password": "$2b$12$VBJFBBwpnnvb9dy.NHdPnOcliuN1pkOPBUMHkfNX8cFJWjl8GlM5O"},  # password = password
    "bestAdmin": {"username": "bestAdmin",
                  "is_admin": True,
                  "hashed_password": "$2b$12$VBJFBBwpnnvb9dy.NHdPnOcliuN1pkOPBUMHkfNX8cFJWjl8GlM5O"}  # password = password
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str) -> User:
    if username in db:
        return User(**db[username])


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def is_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough privileges")
    return user


def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

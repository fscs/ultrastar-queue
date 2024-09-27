from sqlmodel.ext.asyncio.session import AsyncSession

from .models import User
from .utils import verify_password


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    user = await session.get(User, username)
    return user


async def add_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#hash-and-verify-the-passwords
async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
    user = await get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

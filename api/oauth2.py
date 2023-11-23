from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from api.models.user import User as UserModel
from api.types.oauth2 import JwtUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    isSame: bool = pwd_context.verify(plain_password, hashed_password)
    return isSame


def get_password_hash(password: str) -> str:
    hashed_password: str = pwd_context.hash(password)
    return hashed_password


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> UserModel | None:
    user = await user_cruds.fetch_user_by_name(db, username)
    if user is None:
        return None
    if not verify_password(password, user.password):
        return None
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> JwtUser:
    return {"name": "test"}

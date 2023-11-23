from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from api.db.db import get_db
from api.errors import CredentialsException
from api.models.user import User as UserModel
from api.settings import SECRET_KEY
from api.types.oauth2 import JwtUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserModel:
    try:
        payload: JwtUser = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise CredentialsException()
    except JWTError:
        raise CredentialsException()
    user = await user_cruds.fetch_user_by_name(db, payload["name"])
    if user is None:
        raise CredentialsException()
    return user

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import user as user_cruds
from api.db.db import get_db
from api.errors import (
    CredentialsException,
    ExpiredSignatureException,
    NoBearerHeaderException,
)
from api.models.user import User as UserModel
from api.settings import SECRET_KEY
from api.types.oauth2 import JwtUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserModel:
    if token is None:
        raise NoBearerHeaderException()
    try:
        payload: JwtUser = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise CredentialsException()
    except ExpiredSignatureError:
        raise ExpiredSignatureException()
    except JWTError:
        raise CredentialsException()
    user = await user_cruds.fetch_user_by_id(db, payload["sub"])
    if user is None:
        raise CredentialsException()
    return user

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from api.types.oauth2 import JwtUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> JwtUser:
    return {"name": "test"}

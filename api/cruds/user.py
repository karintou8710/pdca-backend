from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.errors import NoUserException, UserAlreadyExistException
from api.models.user import User as UserModel
from api.oauth2 import get_password_hash
from api.schemas.user import SignUp, UserUpdate


async def fetch_user_by_id(db: AsyncSession, id: str) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.id == id)
    user = (await db.scalars(stmt)).first()
    return user


async def fetch_user_by_name(db: AsyncSession, name: str) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.name == name)
    # nameはユニークなので高々一つ
    user = (await db.scalars(stmt)).first()
    return user


async def create_user(db: AsyncSession, sign_up: SignUp) -> UserModel:
    user = UserModel(name=sign_up.name, password=get_password_hash(sign_up.password))
    db.add(user)

    await db.flush()
    await db.refresh(user)
    return user


async def update_user(
    db: AsyncSession, user_update: UserUpdate, user_id: str
) -> UserModel:
    user = await fetch_user_by_id(db, user_id)
    if user is None:
        raise NoUserException()
    same_name_user = await fetch_user_by_name(db, user_update.name)
    if same_name_user is not None and user_id != same_name_user.id:
        raise UserAlreadyExistException()

    user.name = user_update.name
    user.updated_at = datetime.now()
    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: str) -> None:
    user = await fetch_user_by_id(db, user_id)
    if user is None:
        raise NoUserException()
    await db.delete(user)

    await db.flush()

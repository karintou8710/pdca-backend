from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import User as UserModel
from api.oauth2 import get_password_hash
from api.schemas.user import SignUp


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

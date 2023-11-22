from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import User as UserModel
from api.schemas.user import SignUp


async def fetch_user_by_name(db: AsyncSession, name: str) -> UserModel | None:
    stmt = select(UserModel).where(UserModel.name == name)
    # nameはユニークなので高々一つ
    user = (await db.scalars(stmt)).first()
    return user


async def create_user(db: AsyncSession, sign_up: SignUp) -> UserModel:
    user = UserModel(**sign_up.dict())
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user

from sqlalchemy.ext.asyncio import AsyncSession

from api.models.user import User as UserModel
from api.schemas.user import SignUp


async def create_user(db: AsyncSession, sign_up: SignUp) -> UserModel:
    task = UserModel(**sign_up.dict())
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task

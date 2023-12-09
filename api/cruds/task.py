from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.task import Task as TaskModel


async def fetch_tasks_by_uid(db: AsyncSession, user_id: str) -> list[TaskModel]:
    stmt = select(TaskModel).where(TaskModel.user_id == user_id)
    task_seq = (await db.scalars(stmt)).all()
    tasks = list(task_seq)
    return tasks

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.task import Task as TaskModel
from api.schemas import task as task_schema


async def fetch_tasks_by_uid(db: AsyncSession, user_id: str) -> list[TaskModel]:
    stmt = select(TaskModel).where(TaskModel.user_id == user_id)
    task_seq = (await db.scalars(stmt)).all()
    tasks = list(task_seq)
    return tasks


async def create_task(
    db: AsyncSession, user_id: str, param: task_schema.CreateTask
) -> TaskModel:
    task = TaskModel(user_id=user_id, title=param.title)
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task

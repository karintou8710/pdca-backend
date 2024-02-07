from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import task as task_cruds


async def is_own_task(db: AsyncSession, user_id: str, task_id: str) -> bool:
    task = await task_cruds.fetch_tasks_by_id(db, task_id)
    return task is not None and task.user_id == user_id

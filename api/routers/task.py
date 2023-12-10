from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import task as task_crud
from api.db.db import get_db
from api.dependencies import get_current_user
from api.errors import NoTaskException
from api.models.user import User as UserModel
from api.schemas import task as task_schema

router = APIRouter()


@router.get("/users/me/tasks", response_model=list[task_schema.Task])
async def read_my_tasks(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[task_schema.Task]:
    tasks = await task_crud.fetch_tasks_by_uid(db, current_user.id)
    return [task_schema.Task.model_validate(task) for task in tasks]


@router.post(
    "/tasks", response_model=task_schema.Task, status_code=status.HTTP_201_CREATED
)
async def create_task(
    create_body: task_schema.CreateTask,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> task_schema.Task:
    task = await task_crud.create_task(db, current_user.id, create_body)
    return task_schema.Task.model_validate(task)


@router.put(
    "/tasks/{task_id}", response_model=task_schema.Task, status_code=status.HTTP_200_OK
)
async def update_task(
    task_id: str,
    update_body: task_schema.UpdateTask,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> task_schema.Task:
    existed_task = await task_crud.fetch_tasks_by_id(db, task_id)
    if existed_task is None:
        raise NoTaskException()

    task = await task_crud.update_task(db, task_id, update_body)
    return task_schema.Task.model_validate(task)

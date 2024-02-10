from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.cruds import pdca as pdca_cruds
from api.cruds import task as task_cruds
from api.db.db import get_db
from api.dependencies import get_current_user
from api.errors import ForbiddenException, NoTaskException
from api.models.user import User as UserModel
from api.permissions import is_own_task
from api.schemas import pdca as pdca_schema

router = APIRouter()

pdca_sample = pdca_schema.Pdca(
    id="test",
    task_id="test",
    plan_content="a",
    do_content="a",
    check_content="a",
    action_content="a",
)


@router.get("/tasks/{task_id}/pdca", response_model=list[pdca_schema.Pdca])
async def read_my_pdca_list(
    task_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[pdca_schema.Pdca]:
    task = await task_cruds.fetch_tasks_by_id(db, task_id)
    if task is None:
        raise NoTaskException()

    if not await is_own_task(db, current_user.id, task_id):
        raise ForbiddenException()

    pdca_list = await pdca_cruds.fetch_pdca_list_by_task_id(db, task_id)
    return [pdca_schema.Pdca.model_validate(pdca) for pdca in pdca_list]


@router.post(
    "/pdca", response_model=pdca_schema.Pdca, status_code=status.HTTP_201_CREATED
)
async def create_pdca(
    create_body: pdca_schema.CreatePdca,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> pdca_schema.Pdca:
    task = await task_cruds.fetch_tasks_by_id(db, create_body.task_id)
    if task is None:
        raise NoTaskException()

    if not await is_own_task(db, current_user.id, create_body.task_id):
        raise ForbiddenException()

    pdca_model = await pdca_cruds.create_pdca(db, create_body)

    return pdca_schema.Pdca.model_validate(pdca_model)


@router.put("/pdca/{pdca_id}", response_model=pdca_schema.Pdca)
async def update_pdca(
    pdca_id: str,
    update_body: pdca_schema.UpdatePdca,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> pdca_schema.Pdca:
    return pdca_sample


@router.delete("/pdca/{pdca_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pdca(
    pdca_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    return


@router.post("/pdca/{pdca_id}", response_model=pdca_schema.Pdca)
async def read_detail_pdca(
    pdca_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> pdca_schema.Pdca:
    return pdca_sample

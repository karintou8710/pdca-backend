from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.pdca import Pdca as PdcaModel
from api.schemas import pdca as pdca_schema


async def fetch_pdca_list_by_task_id(db: AsyncSession, task_id: str) -> list[PdcaModel]:
    stmt = select(PdcaModel).where(PdcaModel.task_id == task_id)
    pdca_seq = (await db.scalars(stmt)).all()
    pdca_list = list(pdca_seq)
    return pdca_list


async def fetch_pdca_by_id(db: AsyncSession, pdca_id: str) -> PdcaModel | None:
    pdca = await db.get(PdcaModel, pdca_id)
    return pdca


async def create_pdca(
    db: AsyncSession, create_body: pdca_schema.CreatePdca
) -> PdcaModel:
    pdca = PdcaModel(
        task_id=create_body.task_id,
        plan_content=create_body.plan_content,
        do_content=create_body.do_content,
        check_content=create_body.check_content,
        action_content=create_body.action_content,
    )
    db.add(pdca)
    await db.flush()
    await db.refresh(pdca)

    return pdca

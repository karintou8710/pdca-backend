from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.models.pdca import Pdca as PdcaModel


async def fetch_pdca_list_by_task_id(db: AsyncSession, task_id: str) -> list[PdcaModel]:
    stmt = select(PdcaModel).where(PdcaModel.task_id == task_id)
    pdca_seq = (await db.scalars(stmt)).all()
    pdca_list = list(pdca_seq)
    return pdca_list


async def fetch_pdca_by_id(db: AsyncSession, pdca_id: str) -> PdcaModel | None:
    pdca = await db.get(PdcaModel, pdca_id)
    return pdca

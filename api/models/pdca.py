from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base

if TYPE_CHECKING:
    from api.models.task import Task


class Pdca(Base):
    __tablename__ = "pdca"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()")
    )
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"))
    plan_content: Mapped[str] = mapped_column(String(200), nullable=False)
    do_content: Mapped[str] = mapped_column(String(200), nullable=False)
    check_content: Mapped[str] = mapped_column(String(200), nullable=False)
    action_content: Mapped[str] = mapped_column(String(200), nullable=False)

    task: Mapped["Task"] = relationship(back_populates="pdca")

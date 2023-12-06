from typing import TYPE_CHECKING

from sqlalchemy import String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.db.base import Base

if TYPE_CHECKING:
    from api.models.task import Task


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)

    tasks: Mapped[list["Task"]] = relationship(back_populates="user")

from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=datetime.now(),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            default=datetime.now(),
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False,
        )

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.associations import task_tag
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.task import Task


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(
        secondary=task_tag,
        back_populates="tags",
    )

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.associations import task_language
from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.submission import Submission
    from backend.app.models.task import Task


class ProgramLanguage(Base):
    __tablename__ = "program_language"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    display_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    tasks: Mapped[list["Task"]] = relationship(
        secondary=task_language,
        back_populates="languages",
    )
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="program_language",
    )

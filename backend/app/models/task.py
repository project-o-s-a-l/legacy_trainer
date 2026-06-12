from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.associations import task_language, task_tag
from backend.app.db.base import Base
from backend.app.db.enums import TaskDifficulty, TaskStatus

if TYPE_CHECKING:
    from backend.app.models.program_language import ProgramLanguage
    from backend.app.models.submission import Submission
    from backend.app.models.task_check_rule import TaskCheckRule
    from backend.app.models.task_scenario import TaskScenario
    from backend.app.models.tag import Tag
    from backend.app.models.user import User
    from backend.app.models.user_task_progress import UserTaskProgress


class Task(Base):
    __tablename__ = "task"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    legacy_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[TaskDifficulty] = mapped_column(
        Enum(TaskDifficulty, name="task_difficulty"),
        nullable=False,
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.DRAFT,
    )
    max_score: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    tags: Mapped[list["Tag"]] = relationship(
        secondary=task_tag,
        back_populates="tasks",
    )
    languages: Mapped[list["ProgramLanguage"]] = relationship(
        secondary=task_language,
        back_populates="tasks",
    )
    users_progress: Mapped[list["UserTaskProgress"]] = relationship(
        back_populates="task",
    )
    author: Mapped["User"] = relationship(back_populates="tasks")
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="task",
    )
    scenarios: Mapped[list["TaskScenario"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    check_rules: Mapped[list["TaskCheckRule"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )

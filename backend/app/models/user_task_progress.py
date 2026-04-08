from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.submission import Submission
    from backend.app.models.task import Task
    from backend.app.models.user import User


class UserTaskProgress(Base):
    __tablename__ = "user_task_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "task_id", name="uq_user_task_progress"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), nullable=False)
    best_submission_id: Mapped[int] = mapped_column(
        ForeignKey("submission.id"),
        nullable=False,
    )
    attempts_count: Mapped[int] = mapped_column(nullable=False)
    first_submission_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    last_submission_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    is_solved: Mapped[bool] = mapped_column(default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="task_progresses")
    task: Mapped["Task"] = relationship(back_populates="users_progress")
    best_submission: Mapped["Submission"] = relationship(
        back_populates="best_for_progresses",
    )

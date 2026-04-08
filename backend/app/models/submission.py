from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.db.enums import SubmissionStatus

if TYPE_CHECKING:
    from backend.app.models.ai_review import AIReview
    from backend.app.models.program_language import ProgramLanguage
    from backend.app.models.submission_check import SubmissionCheck
    from backend.app.models.task import Task
    from backend.app.models.user import User
    from backend.app.models.user_task_progress import UserTaskProgress


class Submission(Base):
    __tablename__ = "submission"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    language_id: Mapped[int] = mapped_column(
        ForeignKey("program_language.id"),
        nullable=False,
    )
    source_code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        Enum(SubmissionStatus, name="submission_status"),
        nullable=False,
        default=SubmissionStatus.PENDING,
    )
    score: Mapped[int | None] = mapped_column(nullable=True)
    checked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    memory_used_kb: Mapped[int | None] = mapped_column(nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    checks: Mapped[list["SubmissionCheck"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
    )
    ai_reviews: Mapped[list["AIReview"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
    )
    program_language: Mapped["ProgramLanguage"] = relationship(
        back_populates="submissions",
    )
    task: Mapped["Task"] = relationship(back_populates="submissions")
    best_for_progresses: Mapped[list["UserTaskProgress"]] = relationship(
        back_populates="best_submission",
    )
    user: Mapped["User"] = relationship(back_populates="submissions")

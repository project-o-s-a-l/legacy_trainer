from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.db.enums import CheckStatus, SubmissionCheckType

if TYPE_CHECKING:
    from backend.app.models.submission import Submission


class SubmissionCheck(Base):
    __tablename__ = "submission_check"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submission.id"), nullable=False)
    check_type: Mapped[SubmissionCheckType] = mapped_column(
        Enum(SubmissionCheckType, name="submission_check_type"),
        nullable=False,
    )
    status: Mapped[CheckStatus] = mapped_column(
        Enum(CheckStatus, name="check_status"),
        nullable=False,
    )
    report_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    score: Mapped[int] = mapped_column(nullable=False)

    submission: Mapped["Submission"] = relationship(back_populates="checks")

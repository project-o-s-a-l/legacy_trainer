from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.db.enums import SubmissionCheckType

if TYPE_CHECKING:
    from backend.app.models.task import Task


class TaskCheckSpec(Base):
    __tablename__ = "task_check_spec"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), nullable=False)
    check_type: Mapped[SubmissionCheckType] = mapped_column(
        Enum(SubmissionCheckType, name="submission_check_type"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[int] = mapped_column(nullable=False, default=100)
    timeout_seconds: Mapped[int] = mapped_column(nullable=False, default=10)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    order: Mapped[int] = mapped_column(nullable=False, default=0)
    config_json: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    task: Mapped["Task"] = relationship(back_populates="check_specs")

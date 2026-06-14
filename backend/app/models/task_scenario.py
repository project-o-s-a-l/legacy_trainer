from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.task import Task


class TaskScenario(Base):
    __tablename__ = "task_scenario"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("task.id"), nullable=False)
    language_name: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order_index: Mapped[int] = mapped_column(nullable=False, default=0)
    weight: Mapped[int] = mapped_column(nullable=False, default=1)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    expected_output: Mapped[dict[str, Any] | list[Any] | str | int | float | bool | None] = mapped_column(
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    task: Mapped["Task"] = relationship(back_populates="scenarios")

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.db.enums import UserRole

if TYPE_CHECKING:
    from backend.app.models.submission import Submission
    from backend.app.models.task import Task
    from backend.app.models.user_task_progress import UserTaskProgress


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(35), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    login: Mapped[str] = mapped_column(String(55), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    total_score: Mapped[int] = mapped_column(default=0, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.USER,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    avatar_url: Mapped[str | None] = mapped_column(nullable=True)

    tasks: Mapped[list["Task"]] = relationship(back_populates="author")
    task_progresses: Mapped[list["UserTaskProgress"]] = relationship(
        back_populates="user",
    )
    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="user",
    )
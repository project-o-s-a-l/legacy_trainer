from sqlalchemy import Column, ForeignKey, Table

from backend.app.db.base import Base


task_language = Table(
    "task_language",
    Base.metadata,
    Column("task_id", ForeignKey("task.id"), primary_key=True),
    Column("language_id", ForeignKey("program_language.id"), primary_key=True),
)


task_tag = Table(
    "task_tag",
    Base.metadata,
    Column("task_id", ForeignKey("task.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

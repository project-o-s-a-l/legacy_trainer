from pydantic import BaseModel


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    requirements: str
    legacyCode: str | None = None
    difficulty: str
    language: str

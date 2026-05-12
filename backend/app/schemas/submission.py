from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SubmissionCreateRequest(BaseModel):
    code: str = Field(min_length=1)
    language: str = Field(min_length=1, max_length=50)


class SubmissionCreateResponse(BaseModel):
    submissionId: int
    taskId: int
    status: str
    score: int
    message: str
    testPassed: int


class SubmissionResponse(BaseModel):
    id: int
    taskId: int
    userId: int
    language: str
    status: str
    score: int | None = None
    submittedAt: datetime
    checkedAt: datetime | None = None
    memoryUsedKb: int | None = None
    executionTimeMs: int | None = None


class SubmissionCheckResponse(BaseModel):
    id: int
    checkType: str
    status: str
    score: int
    report: dict[str, Any]
    createdAt: datetime

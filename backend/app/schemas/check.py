from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.app.db.enums import CheckStatus, SubmissionCheckType


class TaskCheckSpecContract(BaseModel):
    id: int | None = None
    task_id: int
    check_type: SubmissionCheckType
    name: str
    weight: int = Field(default=100, ge=0)
    timeout_seconds: int = Field(default=10, gt=0)
    is_required: bool = True
    order: int = Field(default=0, ge=0)
    config_json: dict[str, Any] = Field(default_factory=dict)


class CheckReportDetail(BaseModel):
    name: str
    status: CheckStatus
    message: str | None = None
    path: str | None = None
    line: int | None = Field(default=None, ge=1)
    column: int | None = Field(default=None, ge=1)
    details: dict[str, Any] = Field(default_factory=dict)


class CheckReport(BaseModel):
    total: int = Field(default=0, ge=0)
    passed: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    errors: int = Field(default=0, ge=0)
    summary: str | None = None
    details: list[CheckReportDetail] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    artifacts: dict[str, Any] = Field(default_factory=dict)


class InternalCheckResult(BaseModel):
    check_type: SubmissionCheckType
    status: CheckStatus
    score: int = Field(ge=0, le=100)
    report: CheckReport
    spec_id: int | None = None
    name: str | None = None
    weight: int = Field(default=100, ge=0)
    is_required: bool = True
    started_at: datetime | None = None
    finished_at: datetime | None = None
    execution_time_ms: int | None = Field(default=None, ge=0)
    memory_used_kb: int | None = Field(default=None, ge=0)

    def to_report_json(self) -> dict[str, Any]:
        return self.report.model_dump(mode="json")

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from backend.app.db.enums import CheckStatus, SubmissionCheckType, SubmissionStatus
from backend.app.models.program_language import ProgramLanguage
from backend.app.models.submission import Submission
from backend.app.models.submission_check import SubmissionCheck


class SubmissionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_language_by_name_or_display_name(
            self,
            *,
            name: str,
            display_name: str,
    ) -> ProgramLanguage | None:
        stmt = select(ProgramLanguage).where(
            or_(
                ProgramLanguage.name == name,
                ProgramLanguage.display_name == display_name,
            )
        )
        return self.db.scalar(stmt)

    def create_submission(
            self,
            *,
            task_id: int,
            user_id: int,
            language_id: int,
            source_code: str,
    ) -> Submission:
        submission = Submission(
            task_id=task_id,
            user_id=user_id,
            language_id=language_id,
            source_code=source_code,
            status=SubmissionStatus.PENDING,
        )
        self.db.add(submission)
        self.db.flush()
        self.db.refresh(submission)
        return submission

    def create_submission_check(
            self,
            *,
            submission_id: int,
            check_type: SubmissionCheckType,
            status: CheckStatus,
            score: int,
            report_json: dict,
    ) -> SubmissionCheck:
        check = SubmissionCheck(
            submission_id=submission_id,
            check_type=check_type,
            status=status,
            score=score,
            report_json=report_json,
        )
        self.db.add(check)
        self.db.flush()
        self.db.refresh(check)
        return check

    def get_submission_by_id(self, submission_id: int) -> Submission | None:
        stmt = (
            select(Submission)
            .options(
                selectinload(Submission.program_language),
                selectinload(Submission.checks),
            )
            .where(Submission.id == submission_id)
        )
        return self.db.scalar(stmt)

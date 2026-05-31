from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.enums import VerificationFlow
from backend.app.models.verification_session import VerificationSession


class VerificationSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_sessions(
        self,
        *,
        email: str,
        flow: VerificationFlow,
    ) -> list[VerificationSession]:
        stmt = (
            select(VerificationSession)
            .where(
                VerificationSession.email == email,
                VerificationSession.flow == flow,
                VerificationSession.verified_at.is_(None),
                VerificationSession.consumed_at.is_(None),
            )
            .order_by(VerificationSession.id.desc())
        )
        return list(self.db.scalars(stmt).all())

    def mark_sessions_as_consumed(
        self,
        sessions: list[VerificationSession],
    ) -> None:
        now = datetime.now(timezone.utc)
        for session in sessions:
            session.consumed_at = now
            session.updated_at = now

    def create_session(
        self,
        *,
        user_id: int | None,
        email: str,
        flow: VerificationFlow,
        code_hash: str,
        expires_at: datetime,
        registration_username: str | None = None,
        registration_password_hash: str | None = None,
    ) -> VerificationSession:
        session = VerificationSession(
            user_id=user_id,
            email=email,
            flow=flow,
            code_hash=code_hash,
            expires_at=expires_at,
            registration_username=registration_username,
            registration_password_hash=registration_password_hash,
        )
        self.db.add(session)
        self.db.flush()
        self.db.refresh(session)
        return session
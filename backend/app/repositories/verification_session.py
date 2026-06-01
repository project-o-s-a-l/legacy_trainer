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

    def get_latest_active_session(
            self,
            *,
            email: str,
            flow: VerificationFlow,
    ) -> VerificationSession | None:
        stmt = (
            select(VerificationSession)
            .where(
                VerificationSession.email == email,
                VerificationSession.flow == flow,
                VerificationSession.verified_at.is_(None),
                VerificationSession.consumed_at.is_(None),
            )
            .order_by(VerificationSession.id.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def get_session_by_reset_token(
            self,
            *,
            email: str,
            reset_token_hash: str,
    ) -> VerificationSession | None:
        stmt = (
            select(VerificationSession)
            .where(
                VerificationSession.email == email,
                VerificationSession.flow == VerificationFlow.RECOVERY,
                VerificationSession.reset_token_hash == reset_token_hash,
            )
            .order_by(VerificationSession.id.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)

    def mark_sessions_as_consumed(
            self,
            sessions: list[VerificationSession],
    ) -> None:
        now = datetime.now(timezone.utc)
        for session in sessions:
            session.consumed_at = now
            session.updated_at = now

    def increment_attempts(self, session: VerificationSession) -> None:
        session.attempts_count += 1
        session.updated_at = datetime.now(timezone.utc)

    def mark_session_as_verified(self, session: VerificationSession) -> None:
        now = datetime.now(timezone.utc)
        session.verified_at = now
        session.consumed_at = now
        session.updated_at = now

    def attach_reset_token(
            self,
            session: VerificationSession,
            *,
            reset_token_hash: str,
            reset_token_expires_at: datetime,
    ) -> None:
        now = datetime.now(timezone.utc)
        session.verified_at = now
        session.consumed_at = now
        session.reset_token_hash = reset_token_hash
        session.reset_token_expires_at = reset_token_expires_at
        session.updated_at = now

    def create_session(
            self,
            *,
            user_id: int | None,
            email: str,
            flow: VerificationFlow,
            code_hash: str,
            expires_at: datetime,
    ) -> VerificationSession:
        session = VerificationSession(
            user_id=user_id,
            email=email,
            flow=flow,
            code_hash=code_hash,
            expires_at=expires_at,
        )
        self.db.add(session)
        self.db.flush()
        self.db.refresh(session)
        return session

    def clear_reset_token(self, session: VerificationSession) -> None:
        session.reset_token_hash = None
        session.reset_token_expires_at = None
        session.updated_at = datetime.now(timezone.utc)

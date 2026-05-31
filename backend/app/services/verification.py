from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.enums import VerificationFlow
from backend.app.repositories.user import UserRepository
from backend.app.repositories.verification_session import (
    VerificationSessionRepository,
)
from backend.app.schemas.verification import (
    RequestVerificationCodeRequest,
    RequestVerificationCodeResponse,
)
from backend.app.services.email import EmailService


class VerificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.sessions = VerificationSessionRepository(db)
        self.email = EmailService()

    def request_code(
        self,
        data: RequestVerificationCodeRequest,
    ) -> RequestVerificationCodeResponse:
        email = data.email.strip().lower()

        if data.flow == VerificationFlow.REGISTRATION:
            self._request_registration_code(email)
            return RequestVerificationCodeResponse()

        if data.flow == VerificationFlow.RECOVERY:
            self._request_recovery_code(email)
            return RequestVerificationCodeResponse()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported verification flow",
        )

    def _request_registration_code(self, email: str) -> None:
        user = self.users.get_by_email(email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if self.users.is_email_verified(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified",
            )

        active_sessions = self.sessions.get_active_sessions(
            email=email,
            flow=VerificationFlow.REGISTRATION,
        )
        if active_sessions:
            self.sessions.mark_sessions_as_consumed(active_sessions)

        code = self._generate_code()
        code_hash = self._hash_secret(code)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.verification_code_ttl_minutes
        )

        try:
            self.email.send_verification_code(
                email=email,
                code=code,
                flow=VerificationFlow.REGISTRATION,
            )
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to send verification code",
            ) from exc

        self.sessions.create_session(
            user_id=user.id,
            email=email,
            flow=VerificationFlow.REGISTRATION,
            code_hash=code_hash,
            expires_at=expires_at,
        )
        self.db.commit()

    def _request_recovery_code(self, email: str) -> None:
        user = self.users.get_by_email(email)
        if user is None:
            return

        if not self.users.is_email_verified(user):
            return

        active_sessions = self.sessions.get_active_sessions(
            email=email,
            flow=VerificationFlow.RECOVERY,
        )
        if active_sessions:
            self.sessions.mark_sessions_as_consumed(active_sessions)

        code = self._generate_code()
        code_hash = self._hash_secret(code)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.verification_code_ttl_minutes
        )

        try:
            self.email.send_verification_code(
                email=email,
                code=code,
                flow=VerificationFlow.RECOVERY,
            )
        except Exception as exc:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to send verification code",
            ) from exc

        self.sessions.create_session(
            user_id=user.id,
            email=email,
            flow=VerificationFlow.RECOVERY,
            code_hash=code_hash,
            expires_at=expires_at,
        )
        self.db.commit()

    def _generate_code(self) -> str:
        return str(secrets.randbelow(900000) + 100000)

    def _hash_secret(self, value: str) -> str:
        return hashlib.sha256(
            f"{value}:{settings.secret_key}".encode("utf-8")
        ).hexdigest()
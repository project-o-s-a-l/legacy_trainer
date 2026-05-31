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
from backend.app.schemas.auth import RegisterRequest, RegisterResponse
from backend.app.schemas.verification import (
    RequestVerificationCodeRequest,
    RequestVerificationCodeResponse,
)
from backend.app.services.email import EmailService
from backend.app.services.security import hash_password


class VerificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.sessions = VerificationSessionRepository(db)
        self.email = EmailService()

    def start_registration(
        self,
        data: RegisterRequest,
    ) -> RegisterResponse:
        email = data.email.strip().lower()
        username = data.username.strip()

        if self.users.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        if self.users.get_by_username(username) or self.users.get_by_login(username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )

        self._replace_active_sessions(
            email=email,
            flow=VerificationFlow.REGISTRATION,
        )

        code = self._generate_code()
        code_hash = self._hash_secret(code)
        password_hash = hash_password(data.password)
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
            user_id=None,
            email=email,
            flow=VerificationFlow.REGISTRATION,
            code_hash=code_hash,
            expires_at=expires_at,
            registration_username=username,
            registration_password_hash=password_hash,
        )
        self.db.commit()

        return RegisterResponse(email=email)

    def request_code(
        self,
        data: RequestVerificationCodeRequest,
    ) -> RequestVerificationCodeResponse:
        email = data.email.strip().lower()

        if data.flow == VerificationFlow.REGISTRATION:
            self._resend_registration_code(email)
            return RequestVerificationCodeResponse()

        if data.flow == VerificationFlow.RECOVERY:
            self._request_recovery_code(email)
            return RequestVerificationCodeResponse()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported verification flow",
        )

    def _resend_registration_code(self, email: str) -> None:
        active_sessions = self.sessions.get_active_sessions(
            email=email,
            flow=VerificationFlow.REGISTRATION,
        )

        if not active_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registration session not found",
            )

        latest_session = active_sessions[0]
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
            user_id=None,
            email=email,
            flow=VerificationFlow.REGISTRATION,
            code_hash=code_hash,
            expires_at=expires_at,
            registration_username=latest_session.registration_username,
            registration_password_hash=latest_session.registration_password_hash,
        )
        self.db.commit()

    def _request_recovery_code(self, email: str) -> None:
        user = self.users.get_by_email(email)
        if user is None:
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

    def _replace_active_sessions(
        self,
        *,
        email: str,
        flow: VerificationFlow,
    ) -> None:
        active_sessions = self.sessions.get_active_sessions(email=email, flow=flow)
        if active_sessions:
            self.sessions.mark_sessions_as_consumed(active_sessions)

    def _generate_code(self) -> str:
        return str(secrets.randbelow(900000) + 100000)

    def _hash_secret(self, value: str) -> str:
        return hashlib.sha256(
            f"{value}:{settings.secret_key}".encode("utf-8")
        ).hexdigest()
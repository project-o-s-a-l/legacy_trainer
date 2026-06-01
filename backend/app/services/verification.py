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
    VerifyVerificationCodeRequest,
    VerifyVerificationCodeResponse,
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

    def verify_code(
        self,
        data: VerifyVerificationCodeRequest,
    ) -> VerifyVerificationCodeResponse:
        email = data.email.strip().lower()
        code = data.code.strip()

        if data.flow == VerificationFlow.REGISTRATION:
            return self._verify_registration_code(email, code)

        if data.flow == VerificationFlow.RECOVERY:
            return self._verify_recovery_code(email, code)

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

    def _verify_registration_code(
        self,
        email: str,
        code: str,
    ) -> VerifyVerificationCodeResponse:
        user = self.users.get_by_email(email)
        if user is None:
            self._raise_invalid_code()

        if self.users.is_email_verified(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified",
            )

        session = self._get_valid_active_session(
            email=email,
            flow=VerificationFlow.REGISTRATION,
        )

        if session.user_id is not None and session.user_id != user.id:
            self._raise_invalid_code()

        self._assert_code_matches(session, code)

        self.users.mark_email_as_verified(user)
        self.sessions.mark_session_as_verified(session)
        self.db.commit()

        return VerifyVerificationCodeResponse(
            message="Email verified successfully",
        )

    def _verify_recovery_code(
        self,
        email: str,
        code: str,
    ) -> VerifyVerificationCodeResponse:
        user = self.users.get_by_email(email)
        if user is None or not self.users.is_email_verified(user):
            self._raise_invalid_code()

        session = self._get_valid_active_session(
            email=email,
            flow=VerificationFlow.RECOVERY,
        )

        if session.user_id is not None and session.user_id != user.id:
            self._raise_invalid_code()

        self._assert_code_matches(session, code)

        reset_token = self._generate_reset_token()
        self.sessions.attach_reset_token(
            session,
            reset_token_hash=self._hash_secret(reset_token),
            reset_token_expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=settings.password_reset_token_ttl_minutes),
        )
        self.db.commit()

        return VerifyVerificationCodeResponse(
            message="Verification code confirmed",
            resetToken=reset_token,
        )

    def _get_valid_active_session(
        self,
        *,
        email: str,
        flow: VerificationFlow,
    ):
        session = self.sessions.get_latest_active_session(email=email, flow=flow)
        if session is None:
            self._raise_invalid_code()

        if session.expires_at <= datetime.now(timezone.utc):
            self.sessions.mark_sessions_as_consumed([session])
            self.db.commit()
            self._raise_invalid_code()

        return session

    def _assert_code_matches(self, session, code: str) -> None:
        if session.code_hash != self._hash_secret(code):
            self.sessions.increment_attempts(session)
            self.db.commit()
            self._raise_invalid_code()

    def _raise_invalid_code(self) -> None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code is invalid or expired",
        )

    def _generate_code(self) -> str:
        return str(secrets.randbelow(900000) + 100000)

    def _generate_reset_token(self) -> str:
        return secrets.token_urlsafe(32)

    def _hash_secret(self, value: str) -> str:
        return hashlib.sha256(
            f"{value}:{settings.secret_key}".encode("utf-8")
        ).hexdigest()
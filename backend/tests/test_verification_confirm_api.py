from datetime import datetime, timedelta, timezone
import hashlib

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.enums import UserRole, VerificationFlow
from backend.app.models.user import User
from backend.app.models.verification_session import VerificationSession
from backend.app.services.security import hash_password


def create_user(
    db_session: Session,
    *,
    username: str = "tester",
    email: str = "tester@example.com",
    login: str = "tester",
    password: str = "password123",
    verified: bool = False,
) -> User:
    user = User(
        username=username,
        email=email,
        login=login,
        password_hash=hash_password(password),
        role=UserRole.USER,
        email_verified_at=datetime.now(timezone.utc) if verified else None,
    )
    db_session.add(user)
    db_session.flush()
    db_session.refresh(user)
    return user


def build_code_hash(code: str) -> str:
    return hashlib.sha256(
        f"{code}:{settings.secret_key}".encode("utf-8")
    ).hexdigest()


def create_session(
    db_session: Session,
    *,
    user: User,
    email: str,
    flow: VerificationFlow,
    code: str,
    expires_at: datetime | None = None,
) -> VerificationSession:
    session = VerificationSession(
        user_id=user.id,
        email=email,
        flow=flow,
        code_hash=build_code_hash(code),
        expires_at=expires_at or (datetime.now(timezone.utc) + timedelta(minutes=10)),
    )
    db_session.add(session)
    db_session.flush()
    db_session.refresh(session)
    return session


def get_session(db_session: Session, session_id: int) -> VerificationSession | None:
    stmt = select(VerificationSession).where(VerificationSession.id == session_id)
    return db_session.scalar(stmt)


def test_verify_registration_code_marks_email_as_verified(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="verifyuser",
        email="verify@example.com",
        login="verifyuser",
        verified=False,
    )
    session = create_session(
        db_session,
        user=user,
        email=user.email,
        flow=VerificationFlow.REGISTRATION,
        code="123456",
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/verify-verification-code",
        json={
            "email": user.email,
            "code": "123456",
            "flow": "registration",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Email verified successfully"

    refreshed_user = db_session.scalar(select(User).where(User.id == user.id))
    refreshed_session = get_session(db_session, session.id)

    assert refreshed_user is not None
    assert refreshed_user.email_verified_at is not None
    assert refreshed_session is not None
    assert refreshed_session.verified_at is not None
    assert refreshed_session.consumed_at is not None


def test_verify_registration_code_returns_400_for_invalid_code(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="invaliduser",
        email="invalid@example.com",
        login="invaliduser",
        verified=False,
    )
    session = create_session(
        db_session,
        user=user,
        email=user.email,
        flow=VerificationFlow.REGISTRATION,
        code="123456",
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/verify-verification-code",
        json={
            "email": user.email,
            "code": "000000",
            "flow": "registration",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Verification code is invalid or expired"

    refreshed_session = get_session(db_session, session.id)
    assert refreshed_session is not None
    assert refreshed_session.attempts_count == 1
    assert refreshed_session.verified_at is None
    assert refreshed_session.consumed_at is None


def test_verify_registration_code_returns_400_for_expired_code(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="expireduser",
        email="expired@example.com",
        login="expireduser",
        verified=False,
    )
    session = create_session(
        db_session,
        user=user,
        email=user.email,
        flow=VerificationFlow.REGISTRATION,
        code="123456",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/verify-verification-code",
        json={
            "email": user.email,
            "code": "123456",
            "flow": "registration",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Verification code is invalid or expired"

    refreshed_session = get_session(db_session, session.id)
    assert refreshed_session is not None
    assert refreshed_session.consumed_at is not None


def test_verify_recovery_code_returns_reset_token(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="recoveryuser",
        email="recovery@example.com",
        login="recoveryuser",
        verified=True,
    )
    session = create_session(
        db_session,
        user=user,
        email=user.email,
        flow=VerificationFlow.RECOVERY,
        code="654321",
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/verify-verification-code",
        json={
            "email": user.email,
            "code": "654321",
            "flow": "recovery",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["message"] == "Verification code confirmed"
    assert body["resetToken"]

    refreshed_session = get_session(db_session, session.id)
    assert refreshed_session is not None
    assert refreshed_session.verified_at is not None
    assert refreshed_session.consumed_at is not None
    assert refreshed_session.reset_token_hash == build_code_hash(body["resetToken"])
    assert refreshed_session.reset_token_expires_at is not None


def test_verify_recovery_code_returns_400_when_session_missing(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(
        db_session,
        username="missingrecovery",
        email="missingrecovery@example.com",
        login="missingrecovery",
        verified=True,
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/verify-verification-code",
        json={
            "email": "missingrecovery@example.com",
            "code": "123456",
            "flow": "recovery",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Verification code is invalid or expired"
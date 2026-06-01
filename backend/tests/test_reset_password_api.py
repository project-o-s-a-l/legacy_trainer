from datetime import datetime, timedelta, timezone
import hashlib

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.db.enums import UserRole, VerificationFlow
from backend.app.models.user import User
from backend.app.models.verification_session import VerificationSession
from backend.app.services.security import hash_password, verify_password


def create_user(
    db_session: Session,
    *,
    username: str = "tester",
    email: str = "tester@example.com",
    login: str = "tester",
    password: str = "password123",
    verified: bool = True,
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


def build_hash(value: str) -> str:
    return hashlib.sha256(
        f"{value}:{settings.secret_key}".encode("utf-8")
    ).hexdigest()


def create_recovery_session(
    db_session: Session,
    *,
    user: User,
    email: str,
    reset_token: str,
    expires_at: datetime | None = None,
) -> VerificationSession:
    session = VerificationSession(
        user_id=user.id,
        email=email,
        flow=VerificationFlow.RECOVERY,
        code_hash=build_hash("123456"),
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        verified_at=datetime.now(timezone.utc) - timedelta(minutes=4),
        consumed_at=datetime.now(timezone.utc) - timedelta(minutes=4),
        reset_token_hash=build_hash(reset_token),
        reset_token_expires_at=expires_at
        or (datetime.now(timezone.utc) + timedelta(minutes=30)),
    )
    db_session.add(session)
    db_session.flush()
    db_session.refresh(session)
    return session


def get_user(db_session: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db_session.scalar(stmt)


def get_session(db_session: Session, session_id: int) -> VerificationSession | None:
    stmt = select(VerificationSession).where(VerificationSession.id == session_id)
    return db_session.scalar(stmt)


def test_reset_password_success(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="resetuser",
        email="reset@example.com",
        login="resetuser",
        password="oldpassword123",
        verified=True,
    )
    session = create_recovery_session(
        db_session,
        user=user,
        email=user.email,
        reset_token="reset-token-123",
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": user.email,
            "password": "newpassword123",
            "resetToken": "reset-token-123",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

    db_session.expire_all()

    refreshed_user = get_user(db_session, user.id)
    refreshed_session = get_session(db_session, session.id)

    assert refreshed_user is not None
    assert verify_password("newpassword123", refreshed_user.password_hash)
    assert not verify_password("oldpassword123", refreshed_user.password_hash)

    assert refreshed_session is not None
    assert refreshed_session.reset_token_hash is None
    assert refreshed_session.reset_token_expires_at is None


def test_reset_password_returns_400_for_invalid_token(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="invalidreset",
        email="invalidreset@example.com",
        login="invalidreset",
        verified=True,
    )
    create_recovery_session(
        db_session,
        user=user,
        email=user.email,
        reset_token="valid-token",
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": user.email,
            "password": "newpassword123",
            "resetToken": "wrong-token",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Password reset token is invalid or expired"


def test_reset_password_returns_400_for_expired_token(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="expiredreset",
        email="expiredreset@example.com",
        login="expiredreset",
        verified=True,
    )
    session = create_recovery_session(
        db_session,
        user=user,
        email=user.email,
        reset_token="expired-token",
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": user.email,
            "password": "newpassword123",
            "resetToken": "expired-token",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Password reset token is invalid or expired"

    db_session.expire_all()

    refreshed_session = get_session(db_session, session.id)
    assert refreshed_session is not None
    assert refreshed_session.reset_token_hash is None
    assert refreshed_session.reset_token_expires_at is None


def test_reset_password_token_cannot_be_reused(
    client: TestClient,
    db_session: Session,
) -> None:
    user = create_user(
        db_session,
        username="reuseuser",
        email="reuse@example.com",
        login="reuseuser",
        verified=True,
    )
    create_recovery_session(
        db_session,
        user=user,
        email=user.email,
        reset_token="single-use-token",
    )
    db_session.commit()

    first_response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": user.email,
            "password": "newpassword123",
            "resetToken": "single-use-token",
        },
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": user.email,
            "password": "anotherpassword123",
            "resetToken": "single-use-token",
        },
    )

    assert second_response.status_code == 400
    assert (
        second_response.json()["detail"]
        == "Password reset token is invalid or expired"
    )
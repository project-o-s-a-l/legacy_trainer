from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.enums import UserRole, VerificationFlow
from backend.app.models.user import User
from backend.app.models.verification_session import VerificationSession
from backend.app.services.email import EmailService
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


def get_sessions(
    db_session: Session,
    *,
    email: str,
) -> list[VerificationSession]:
    stmt = select(VerificationSession).where(VerificationSession.email == email)
    return list(db_session.scalars(stmt).all())


def test_request_verification_code_for_registration_success(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    sent_messages: list[tuple[str, str, VerificationFlow]] = []

    def fake_send(self, *, email: str, code: str, flow: VerificationFlow) -> None:
        sent_messages.append((email, code, flow))

    monkeypatch.setattr(EmailService, "send_verification_code", fake_send)

    user = create_user(
        db_session,
        username="newuser",
        email="newuser@example.com",
        login="newuser",
        verified=False,
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/request-verification-code",
        json={
            "email": user.email,
            "flow": "registration",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Verification code sent successfully"

    sessions = get_sessions(db_session, email=user.email)
    assert len(sessions) == 1
    assert sessions[0].user_id == user.id
    assert sessions[0].flow == VerificationFlow.REGISTRATION
    assert sessions[0].verified_at is None
    assert sessions[0].consumed_at is None

    assert len(sent_messages) == 1
    assert sent_messages[0][0] == user.email
    assert sent_messages[0][2] == VerificationFlow.REGISTRATION
    assert len(sent_messages[0][1]) == 6


def test_request_verification_code_for_registration_returns_404_when_user_missing(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/request-verification-code",
        json={
            "email": "missing@example.com",
            "flow": "registration",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_request_verification_code_for_registration_returns_400_when_already_verified(
    client: TestClient,
    db_session: Session,
) -> None:
    create_user(
        db_session,
        username="verified",
        email="verified@example.com",
        login="verified",
        verified=True,
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/request-verification-code",
        json={
            "email": "verified@example.com",
            "flow": "registration",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email is already verified"


def test_request_verification_code_for_recovery_success(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    sent_messages: list[tuple[str, str, VerificationFlow]] = []

    def fake_send(self, *, email: str, code: str, flow: VerificationFlow) -> None:
        sent_messages.append((email, code, flow))

    monkeypatch.setattr(EmailService, "send_verification_code", fake_send)

    user = create_user(
        db_session,
        username="recovery",
        email="recovery@example.com",
        login="recovery",
        verified=True,
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/request-verification-code",
        json={
            "email": user.email,
            "flow": "recovery",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Verification code sent successfully"

    sessions = get_sessions(db_session, email=user.email)
    assert len(sessions) == 1
    assert sessions[0].user_id == user.id
    assert sessions[0].flow == VerificationFlow.RECOVERY

    assert len(sent_messages) == 1
    assert sent_messages[0][2] == VerificationFlow.RECOVERY


def test_request_verification_code_for_recovery_returns_200_when_user_missing(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    sent_messages: list[tuple[str, str, VerificationFlow]] = []

    def fake_send(self, *, email: str, code: str, flow: VerificationFlow) -> None:
        sent_messages.append((email, code, flow))

    monkeypatch.setattr(EmailService, "send_verification_code", fake_send)

    response = client.post(
        "/api/v1/auth/request-verification-code",
        json={
            "email": "unknown@example.com",
            "flow": "recovery",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Verification code sent successfully"

    sessions = get_sessions(db_session, email="unknown@example.com")
    assert sessions == []
    assert sent_messages == []


def test_request_verification_code_for_recovery_returns_200_for_unverified_user(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    sent_messages: list[tuple[str, str, VerificationFlow]] = []

    def fake_send(self, *, email: str, code: str, flow: VerificationFlow) -> None:
        sent_messages.append((email, code, flow))

    monkeypatch.setattr(EmailService, "send_verification_code", fake_send)

    create_user(
        db_session,
        username="pending",
        email="pending@example.com",
        login="pending",
        verified=False,
    )
    db_session.commit()

    response = client.post(
        "/api/v1/auth/request-verification-code",
        json={
            "email": "pending@example.com",
            "flow": "recovery",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Verification code sent successfully"

    sessions = get_sessions(db_session, email="pending@example.com")
    assert sessions == []
    assert sent_messages == []


def test_request_verification_code_replaces_previous_active_session(
    client: TestClient,
    db_session: Session,
    monkeypatch,
) -> None:
    def fake_send(self, *, email: str, code: str, flow: VerificationFlow) -> None:
        return None

    monkeypatch.setattr(EmailService, "send_verification_code", fake_send)

    create_user(
        db_session,
        username="replace",
        email="replace@example.com",
        login="replace",
        verified=False,
    )
    db_session.commit()

    first_response = client.post(
        "/api/v1/auth/request-verification-code",
        json={
            "email": "replace@example.com",
            "flow": "registration",
        },
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/api/v1/auth/request-verification-code",
        json={
            "email": "replace@example.com",
            "flow": "registration",
        },
    )
    assert second_response.status_code == 200

    sessions = get_sessions(db_session, email="replace@example.com")
    assert len(sessions) == 2

    active_sessions = [item for item in sessions if item.consumed_at is None]
    consumed_sessions = [item for item in sessions if item.consumed_at is not None]

    assert len(active_sessions) == 1
    assert len(consumed_sessions) == 1


def test_request_verification_code_returns_422_for_invalid_email(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/request-verification-code",
        json={
            "email": "not-an-email",
            "flow": "registration",
        },
    )

    assert response.status_code == 422
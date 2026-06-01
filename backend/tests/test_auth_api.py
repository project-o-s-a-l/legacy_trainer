from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from backend.app.models.user import User


def build_register_payload(
    *,
    username: str = "tester",
    email: str = "tester@example.com",
    password: str = "password123",
) -> dict:
    return {
        "username": username,
        "email": email,
        "password": password,
    }


def build_login_payload(
    *,
    login: str = "tester",
    password: str = "password123",
) -> dict:
    return {
        "login": login,
        "password": password,
    }


def register_user(
    client: TestClient,
    *,
    username: str = "tester",
    email: str = "tester@example.com",
    password: str = "password123",
):
    response = client.post(
        "/api/v1/auth/register",
        json=build_register_payload(
            username=username,
            email=email,
            password=password,
        ),
    )
    assert response.status_code == 201
    return response


def login_user(
    client: TestClient,
    *,
    login: str = "tester",
    password: str = "password123",
):
    return client.post(
        "/api/v1/auth/login",
        json=build_login_payload(
            login=login,
            password=password,
        ),
    )


def mark_user_verified(db_session, email: str) -> None:
    user = db_session.scalar(select(User).where(User.email == email))
    assert user is not None
    user.email_verified_at = datetime.now(timezone.utc)
    db_session.commit()


def test_register_success(client: TestClient, db_session) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json=build_register_payload(),
    )

    assert response.status_code == 201
    body = response.json()

    assert body["message"] == "User registered successfully"
    assert body["user"]["id"] > 0
    assert body["user"]["username"] == "tester"
    assert body["user"]["email"] == "tester@example.com"

    stmt = select(User).where(User.email == "tester@example.com")
    user = db_session.scalar(stmt)
    assert user is not None
    assert user.email_verified_at is None


def test_register_duplicate_email_for_verified_user(
    client: TestClient,
    db_session,
) -> None:
    register_user(client, username="tester1", email="same@example.com")
    mark_user_verified(db_session, "same@example.com")

    response = client.post(
        "/api/v1/auth/register",
        json=build_register_payload(
            username="tester2",
            email="same@example.com",
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_register_duplicate_username(client: TestClient) -> None:
    register_user(client, username="sameuser", email="first@example.com")

    response = client.post(
        "/api/v1/auth/register",
        json=build_register_payload(
            username="sameuser",
            email="second@example.com",
        ),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_login_requires_verified_email(client: TestClient) -> None:
    register_user(client)

    response = login_user(client)

    assert response.status_code == 403
    assert response.json()["detail"] == "Email is not verified"


def test_login_success_with_username(client: TestClient, db_session) -> None:
    register_user(client)
    mark_user_verified(db_session, "tester@example.com")

    response = login_user(client)

    assert response.status_code == 200
    body = response.json()

    assert body["token"]
    assert body["user"]["id"] > 0
    assert body["user"]["login"] == "tester"
    assert response.cookies.get("access_token") is not None


def test_login_success_with_email(client: TestClient, db_session) -> None:
    register_user(client)
    mark_user_verified(db_session, "tester@example.com")

    response = login_user(client, login="tester@example.com")

    assert response.status_code == 200
    body = response.json()

    assert body["token"]
    assert body["user"]["login"] == "tester"


def test_login_wrong_password(client: TestClient) -> None:
    register_user(client)

    response = login_user(client, password="wrongpass123")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_me_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_me_returns_current_user(client: TestClient, db_session) -> None:
    register_user(client)
    mark_user_verified(db_session, "tester@example.com")
    login_response = login_user(client)

    assert login_response.status_code == 200

    response = client.get("/api/v1/users/me")

    assert response.status_code == 200
    body = response.json()

    assert body["username"] == "tester"
    assert body["email"] == "tester@example.com"
    assert body["points"] == 0
    assert "memberSince" in body
    assert "lastSeen" in body
    assert "avatarUrl" in body
    assert body["isOnline"] is False


def test_logout_clears_auth(client: TestClient, db_session) -> None:
    register_user(client)
    mark_user_verified(db_session, "tester@example.com")
    login_response = login_user(client)

    assert login_response.status_code == 200
    assert client.cookies.get("access_token") is not None

    logout_response = client.post("/api/v1/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logged out"

    me_response = client.get("/api/v1/users/me")

    assert me_response.status_code == 401
    assert me_response.json()["detail"] == "Not authenticated"


def test_register_allows_retry_for_unverified_user(
    client: TestClient,
    db_session,
) -> None:
    first_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "firstuser",
            "email": "retry@example.com",
            "password": "password123",
        },
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "seconduser",
            "email": "retry@example.com",
            "password": "newpassword123",
        },
    )
    assert second_response.status_code == 201

    body = second_response.json()
    assert body["user"]["email"] == "retry@example.com"
    assert body["user"]["username"] == "seconduser"

    stmt = select(User).where(User.email == "retry@example.com")
    user = db_session.scalar(stmt)
    assert user is not None
    assert user.username == "seconduser"
    assert user.login == "seconduser"
    assert user.email_verified_at is None
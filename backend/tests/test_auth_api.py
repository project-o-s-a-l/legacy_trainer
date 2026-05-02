from fastapi.testclient import TestClient


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


def test_register_success(client: TestClient) -> None:
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


def test_register_duplicate_email(client: TestClient) -> None:
    register_user(client, username="tester1", email="same@example.com")

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


def test_login_success_with_username(client: TestClient) -> None:
    register_user(client)

    response = login_user(client)

    assert response.status_code == 200
    body = response.json()

    assert body["token"]
    assert body["user"]["id"] > 0
    assert body["user"]["login"] == "tester"
    assert response.cookies.get("access_token") is not None


def test_login_success_with_email(client: TestClient) -> None:
    register_user(client)

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


def test_me_returns_current_user(client: TestClient) -> None:
    register_user(client)
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


def test_logout_clears_auth(client: TestClient) -> None:
    register_user(client)
    login_response = login_user(client)

    assert login_response.status_code == 200
    assert client.cookies.get("access_token") is not None

    logout_response = client.post("/api/v1/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Logged out"

    me_response = client.get("/api/v1/users/me")

    assert me_response.status_code == 401
    assert me_response.json()["detail"] == "Not authenticated"

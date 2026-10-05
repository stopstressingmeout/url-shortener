def test_register_success(client):
    response = client.post(
        "/auth/register", json={"email": "a@example.com", "password": "password123"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "a@example.com"
    assert "id" in body
    # The password must never be sent back, hashed or not.
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email_returns_409(client):
    payload = {"email": "a@example.com", "password": "password123"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 409


def test_register_duplicate_email_is_case_insensitive(client):
    client.post(
        "/auth/register", json={"email": "a@example.com", "password": "password123"}
    )
    response = client.post(
        "/auth/register", json={"email": "A@Example.com", "password": "password123"}
    )
    assert response.status_code == 409


def test_register_short_password_returns_422(client):
    response = client.post(
        "/auth/register", json={"email": "a@example.com", "password": "short"}
    )
    assert response.status_code == 422


def test_register_invalid_email_returns_422(client):
    response = client.post(
        "/auth/register", json={"email": "not-an-email", "password": "password123"}
    )
    assert response.status_code == 422


def test_login_success_returns_token(client):
    client.post(
        "/auth/register", json={"email": "a@example.com", "password": "password123"}
    )
    response = client.post(
        "/auth/login", data={"username": "a@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_returns_401(client):
    client.post(
        "/auth/register", json={"email": "a@example.com", "password": "password123"}
    )
    response = client.post(
        "/auth/login", data={"username": "a@example.com", "password": "wrong-password"}
    )
    assert response.status_code == 401


def test_login_unknown_email_returns_401(client):
    response = client.post(
        "/auth/login", data={"username": "nobody@example.com", "password": "password123"}
    )
    assert response.status_code == 401


def test_protected_route_without_token_returns_401(client):
    response = client.post("/urls", json={"original_url": "https://example.com/page"})
    assert response.status_code == 401


def test_protected_route_with_garbage_token_returns_401(client):
    response = client.post(
        "/urls",
        json={"original_url": "https://example.com/page"},
        headers={"Authorization": "Bearer this-is-not-a-real-token"},
    )
    assert response.status_code == 401
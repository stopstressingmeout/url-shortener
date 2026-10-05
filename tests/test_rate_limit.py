from app.config import settings


def test_login_is_limited_after_too_many_attempts(client):
    payload = {"username": "x@example.com", "password": "wrong-password"}

    for _ in range(settings.login_rate_limit_requests):
        assert client.post("/auth/login", data=payload).status_code == 401

    response = client.post("/auth/login", data=payload)
    assert response.status_code == 429
    assert "retry-after" in response.headers


def test_general_requests_are_limited(client):
    for _ in range(settings.rate_limit_requests):
        assert client.get("/doesnotexist").status_code == 404

    response = client.get("/doesnotexist")
    assert response.status_code == 429


def test_health_check_is_never_rate_limited(client):
    for _ in range(settings.rate_limit_requests + 20):
        assert client.get("/health").status_code == 200
def test_create_url(client, auth_headers):
    response = client.post(
        "/urls",
        json={"original_url": "https://example.com/some/page"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["original_url"] == "https://example.com/some/page"
    assert len(body["slug"]) == 7
    assert body["short_url"].endswith(body["slug"])


def test_create_url_invalid_url_returns_422(client, auth_headers):
    response = client.post(
        "/urls", json={"original_url": "not a url"}, headers=auth_headers
    )
    assert response.status_code == 422


def test_redirect_sends_user_to_original_url(client, auth_headers):
    created = client.post(
        "/urls",
        json={"original_url": "https://example.com/some/page"},
        headers=auth_headers,
    ).json()

    response = client.get(f"/{created['slug']}", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/some/page"


def test_redirect_works_without_login(client, auth_headers):
    created = client.post(
        "/urls",
        json={"original_url": "https://example.com/public"},
        headers=auth_headers,
    ).json()
    response = client.get(f"/{created['slug']}", follow_redirects=False)
    assert response.status_code == 307


def test_redirect_unknown_slug_returns_404(client):
    response = client.get("/doesnotexist", follow_redirects=False)
    assert response.status_code == 404


def test_list_urls_requires_login(client):
    response = client.get("/urls")
    assert response.status_code == 401


def test_users_only_see_their_own_urls(client, create_user):
    alice = create_user("alice@example.com")
    bob = create_user("bob@example.com")

    client.post("/urls", json={"original_url": "https://example.com/a1"}, headers=alice)
    client.post("/urls", json={"original_url": "https://example.com/a2"}, headers=alice)
    bobs_link = client.post(
        "/urls", json={"original_url": "https://example.com/b1"}, headers=bob
    ).json()

    alice_urls = client.get("/urls", headers=alice).json()
    bob_urls = client.get("/urls", headers=bob).json()

    assert len(alice_urls) == 2
    assert len(bob_urls) == 1
    assert bobs_link["slug"] not in [u["slug"] for u in alice_urls]
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 201
    assert response.json() == {"status": "ok"}
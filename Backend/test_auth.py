from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app import main
from app.auth import hash_password, verify_password


client = TestClient(main.app)


def test_password_hash_is_not_plaintext():
    encoded = hash_password("correct horse battery staple")
    assert encoded != "correct horse battery staple"
    assert verify_password("correct horse battery staple", encoded)
    assert not verify_password("wrong-password", encoded)


def test_register_returns_bearer_token(monkeypatch):
    created = type(
        "User",
        (),
        {"id": 7, "name": "Test Farmer", "email": "test@example.com", "created_at": datetime.now(timezone.utc)},
    )()
    monkeypatch.setattr(main, "get_user_by_email", lambda email: None)
    monkeypatch.setattr(main, "create_user", lambda **kwargs: created)

    response = client.post("/auth/register", json={"name": "Test Farmer", "email": "test@example.com", "password": "password123"})

    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"
    assert response.json()["user"]["email"] == "test@example.com"
    assert response.json()["access_token"]


def test_login_rejects_wrong_password(monkeypatch):
    user = type(
        "User",
        (),
        {"id": 7, "name": "Test Farmer", "email": "test@example.com", "password_hash": hash_password("password123"), "created_at": datetime.now(timezone.utc)},
    )()
    monkeypatch.setattr(main, "get_user_by_email", lambda email: user)

    response = client.post("/auth/login", json={"email": "test@example.com", "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

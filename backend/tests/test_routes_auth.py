"""
Tests for backend/routes/auth.py

Covers:
  - POST /api/auth/register
  - POST /api/auth/login
  - POST /api/auth/logout
"""

import sys
import os
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from middleware.auth import hash_password, create_access_token


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REGISTER_URL = "/api/auth/register"
LOGIN_URL = "/api/auth/login"
LOGOUT_URL = "/api/auth/logout"


def _register_payload(email="new@example.com", password="Pass123!", first_name="Alice"):
    return {"first_name": first_name, "email": email, "password": password}


def _login_payload(email="test@example.com", password="TestPass123!"):
    return {"email": email, "password": password}


# ---------------------------------------------------------------------------
# POST /api/auth/register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_new_user_returns_200_and_token(self, client):
        resp = client.post(REGISTER_URL, json=_register_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_creates_user_with_correct_email(self, client, db):
        from models import User
        email = "created@example.com"
        client.post(REGISTER_URL, json=_register_payload(email=email))
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        assert user.email == email

    def test_register_stores_hashed_password(self, client, db):
        from models import User
        email = "hashed@example.com"
        plain_pw = "MyPlainPassword"
        client.post(REGISTER_URL, json=_register_payload(email=email, password=plain_pw))
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        assert user.password_hash != plain_pw

    def test_register_duplicate_email_returns_400(self, client, sample_user):
        resp = client.post(REGISTER_URL, json=_register_payload(email=sample_user.email))
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_sets_first_name(self, client, db):
        from models import User
        email = "named@example.com"
        client.post(REGISTER_URL, json=_register_payload(email=email, first_name="Bob"))
        user = db.query(User).filter(User.email == email).first()
        assert user.first_name == "Bob"

    def test_register_missing_email_returns_422(self, client):
        resp = client.post(REGISTER_URL, json={"first_name": "A", "password": "Pass"})
        assert resp.status_code == 422

    def test_register_missing_password_returns_422(self, client):
        resp = client.post(REGISTER_URL, json={"first_name": "A", "email": "a@b.com"})
        assert resp.status_code == 422

    def test_register_missing_first_name_returns_422(self, client):
        resp = client.post(REGISTER_URL, json={"email": "a@b.com", "password": "Pass"})
        assert resp.status_code == 422

    def test_register_returns_valid_jwt(self, client):
        import jwt as pyjwt
        from middleware.auth import JWT_SECRET_KEY, ALGORITHM
        resp = client.post(REGISTER_URL, json=_register_payload(email="jwt@test.com"))
        token = resp.json()["access_token"]
        payload = pyjwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "jwt@test.com"


# ---------------------------------------------------------------------------
# POST /api/auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_valid_credentials_returns_token(self, client, sample_user):
        resp = client.post(LOGIN_URL, json=_login_payload())
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self, client, sample_user):
        resp = client.post(LOGIN_URL, json=_login_payload(password="WrongPassword"))
        assert resp.status_code == 401
        assert "invalid credentials" in resp.json()["detail"].lower()

    def test_login_nonexistent_email_returns_401(self, client):
        resp = client.post(LOGIN_URL, json=_login_payload(email="nobody@example.com"))
        assert resp.status_code == 401

    def test_login_returns_bearer_token_type(self, client, sample_user):
        resp = client.post(LOGIN_URL, json=_login_payload())
        assert resp.json()["token_type"] == "bearer"

    def test_login_token_contains_user_email(self, client, sample_user):
        import jwt as pyjwt
        from middleware.auth import JWT_SECRET_KEY, ALGORITHM
        resp = client.post(LOGIN_URL, json=_login_payload())
        token = resp.json()["access_token"]
        payload = pyjwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == sample_user.email

    def test_login_missing_email_returns_422(self, client):
        resp = client.post(LOGIN_URL, json={"password": "Pass"})
        assert resp.status_code == 422

    def test_login_missing_password_returns_422(self, client):
        resp = client.post(LOGIN_URL, json={"email": "a@b.com"})
        assert resp.status_code == 422

    def test_login_empty_body_returns_422(self, client):
        resp = client.post(LOGIN_URL, json={})
        assert resp.status_code == 422

    def test_login_case_sensitive_email(self, client, sample_user):
        """Email lookup is case-sensitive in current implementation."""
        resp = client.post(LOGIN_URL, json=_login_payload(email="TEST@EXAMPLE.COM"))
        # Should fail since DB stores lowercase email
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /api/auth/logout
# ---------------------------------------------------------------------------

class TestLogout:
    def test_logout_valid_token_returns_200(self, client, sample_user, auth_token, mock_redis):
        headers = {"Authorization": f"Bearer {auth_token}"}
        with patch("db.redis.redis_client", mock_redis):
            resp = client.post(LOGOUT_URL, headers=headers)
        assert resp.status_code == 200
        assert "logged out" in resp.json()["message"].lower()

    def test_logout_blacklists_token(self, client, sample_user, auth_token, mock_redis):
        headers = {"Authorization": f"Bearer {auth_token}"}
        with patch("db.redis.redis_client", mock_redis):
            resp = client.post(LOGOUT_URL, headers=headers)
        assert resp.status_code == 200
        # cache_set should have been called with a blacklist key
        mock_redis.setex.assert_awaited()

    def test_logout_without_token_returns_401(self, client):
        resp = client.post(LOGOUT_URL)
        assert resp.status_code == 401

    def test_logout_with_invalid_token_returns_401(self, client):
        headers = {"Authorization": "Bearer invalid.token.here"}
        resp = client.post(LOGOUT_URL, headers=headers)
        assert resp.status_code == 401

    def test_logout_with_expired_token_returns_401(self, client, sample_user):
        expired_token = create_access_token(
            {"sub": sample_user.email}, expires_delta=timedelta(seconds=-1)
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        resp = client.post(LOGOUT_URL, headers=headers)
        assert resp.status_code == 401
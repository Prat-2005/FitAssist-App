"""
Tests for backend/middleware/auth.py

Covers:
  - hash_password / verify_password
  - create_access_token / verify_token
  - get_current_user (via dependency injection)
"""

import sys
import os
import uuid
from datetime import timedelta, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import jwt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from middleware.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    JWT_SECRET_KEY,
    ALGORITHM,
)
from fastapi import HTTPException


# ---------------------------------------------------------------------------
# hash_password / verify_password
# ---------------------------------------------------------------------------

class TestHashPassword:
    def test_returns_string(self):
        hashed = hash_password("MySecret123")
        assert isinstance(hashed, str)

    def test_hash_is_different_from_plaintext(self):
        plain = "MySecret123"
        hashed = hash_password(plain)
        assert hashed != plain

    def test_same_password_produces_different_hashes(self):
        """bcrypt generates a unique salt each time."""
        h1 = hash_password("SamePassword")
        h2 = hash_password("SamePassword")
        assert h1 != h2

    def test_hash_starts_with_bcrypt_prefix(self):
        hashed = hash_password("test")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_empty_string_hashed(self):
        hashed = hash_password("")
        assert isinstance(hashed, str)
        assert len(hashed) > 0


class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        plain = "CorrectPassword!"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_wrong_password_returns_false(self):
        hashed = hash_password("CorrectPassword!")
        assert verify_password("WrongPassword!", hashed) is False

    def test_empty_password_against_hashed_empty(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True

    def test_empty_password_against_non_empty_hash_returns_false(self):
        hashed = hash_password("NotEmpty")
        assert verify_password("", hashed) is False

    def test_case_sensitivity(self):
        hashed = hash_password("Password")
        assert verify_password("password", hashed) is False

    def test_unicode_password(self):
        plain = "p@ssw0rd_ünïcödé"
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True

    def test_long_password(self):
        """bcrypt handles passwords up to 72 bytes; verify still works."""
        plain = "A" * 50
        hashed = hash_password(plain)
        assert verify_password(plain, hashed) is True


# ---------------------------------------------------------------------------
# create_access_token
# ---------------------------------------------------------------------------

class TestCreateAccessToken:
    def test_returns_string(self):
        token = create_access_token({"sub": "user@example.com"})
        assert isinstance(token, str)

    def test_token_contains_subject(self):
        email = "user@example.com"
        token = create_access_token({"sub": email})
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == email

    def test_custom_expires_delta(self):
        delta = timedelta(minutes=15)
        token = create_access_token({"sub": "user@example.com"}, expires_delta=delta)
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.utcfromtimestamp(payload["exp"])
        now = datetime.utcnow()
        # Allow a 5-second tolerance
        assert abs((exp - now).total_seconds() - 900) < 5

    def test_default_expiry_is_7_days(self):
        token = create_access_token({"sub": "user@example.com"})
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.utcfromtimestamp(payload["exp"])
        expected = datetime.utcnow() + timedelta(days=7)
        assert abs((exp - expected).total_seconds()) < 5

    def test_additional_claims_preserved(self):
        token = create_access_token({"sub": "u@e.com", "role": "admin"})
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["role"] == "admin"

    def test_token_structure_has_three_parts(self):
        token = create_access_token({"sub": "u@e.com"})
        parts = token.split(".")
        assert len(parts) == 3

    def test_original_data_not_mutated(self):
        data = {"sub": "u@e.com"}
        original = data.copy()
        create_access_token(data)
        assert data == original


# ---------------------------------------------------------------------------
# verify_token
# ---------------------------------------------------------------------------

class TestVerifyToken:
    def test_valid_token_returns_payload(self):
        token = create_access_token({"sub": "u@e.com"})
        payload = verify_token(token)
        assert payload["sub"] == "u@e.com"

    def test_expired_token_raises_401(self):
        token = create_access_token({"sub": "u@e.com"}, expires_delta=timedelta(seconds=-1))
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_invalid_signature_raises_401(self):
        token = create_access_token({"sub": "u@e.com"})
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc_info:
            verify_token(tampered)
        assert exc_info.value.status_code == 401

    def test_completely_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            verify_token("not.a.token")
        assert exc_info.value.status_code == 401

    def test_empty_string_raises_401(self):
        with pytest.raises(HTTPException) as exc_info:
            verify_token("")
        assert exc_info.value.status_code == 401

    def test_www_authenticate_header_present(self):
        token = create_access_token({"sub": "u@e.com"}, expires_delta=timedelta(seconds=-1))
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert "WWW-Authenticate" in exc_info.value.headers

    def test_token_signed_with_different_secret_raises_401(self):
        token = jwt.encode({"sub": "u@e.com", "exp": datetime.utcnow() + timedelta(hours=1)},
                           "different-secret", algorithm=ALGORITHM)
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        assert exc_info.value.status_code == 401


# ---------------------------------------------------------------------------
# get_current_user (async dependency)
# ---------------------------------------------------------------------------

class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self, db, sample_user, auth_token):
        from middleware.auth import get_current_user

        with patch("middleware.auth.cache_get", new=AsyncMock(return_value=None)):
            user = await get_current_user(token=auth_token, db=db)
        assert user.email == sample_user.email

    @pytest.mark.asyncio
    async def test_blacklisted_token_raises_401(self, db, sample_user, auth_token):
        from middleware.auth import get_current_user
        import db.redis as redis_module

        # Simulate blacklisted token
        with patch("middleware.auth.cache_get", new=AsyncMock(return_value="revoked")):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=auth_token, db=db)
            assert exc_info.value.status_code == 401
            assert "revoked" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_token_without_sub_raises_401(self, db):
        from middleware.auth import get_current_user

        # Token without 'sub' claim
        token = create_access_token({"role": "admin"})  # no sub
        with patch("middleware.auth.cache_get", new=AsyncMock(return_value=None)):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=token, db=db)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_nonexistent_user_raises_401(self, db):
        from middleware.auth import get_current_user

        token = create_access_token({"sub": "ghost@example.com"})
        with patch("middleware.auth.cache_get", new=AsyncMock(return_value=None)):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=token, db=db)
            assert exc_info.value.status_code == 401
            assert "not found" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_valid_token_correct_user_returned(self, db, sample_user, auth_token):
        from middleware.auth import get_current_user

        with patch("middleware.auth.cache_get", new=AsyncMock(return_value=None)):
            user = await get_current_user(token=auth_token, db=db)
        assert user.email == sample_user.email
        assert str(user.id) == str(sample_user.id)
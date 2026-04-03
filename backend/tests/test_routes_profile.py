"""
Tests for backend/routes/profile.py

Covers:
  - GET  /api/profile/me
  - PUT  /api/profile/me
  - GET  /api/profile/{user_id}
  - DELETE /api/profile/me
"""

import sys
import os
import uuid

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, Profile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ME_URL = "/api/profile/me"


def _user_url(user_id):
    return f"/api/profile/{user_id}"


def _update_payload(**kwargs):
    defaults = {"fitness_goal": "weight_loss", "experience_level": "beginner"}
    defaults.update(kwargs)
    return defaults


# ---------------------------------------------------------------------------
# GET /api/profile/me
# ---------------------------------------------------------------------------

class TestGetProfile:
    def test_returns_profile_for_authenticated_user(self, authed_client, sample_profile):
        resp = authed_client.get(ME_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["fitness_goal"] == "weight_loss"

    def test_returns_404_when_profile_missing(self, authed_client):
        """Authenticated user exists but has no profile."""
        resp = authed_client.get(ME_URL)
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_response_contains_profile_fields(self, authed_client, sample_profile):
        resp = authed_client.get(ME_URL)
        data = resp.json()
        for field in ("id", "user_id", "fitness_goal", "experience_level"):
            assert field in data

    def test_profile_user_id_matches_current_user(self, authed_client, sample_user, sample_profile):
        resp = authed_client.get(ME_URL)
        assert resp.json()["user_id"] == str(sample_user.id)


# ---------------------------------------------------------------------------
# PUT /api/profile/me
# ---------------------------------------------------------------------------

class TestUpdateProfile:
    def test_creates_profile_if_not_exists(self, authed_client, db, sample_user):
        resp = authed_client.put(ME_URL, json=_update_payload(fitness_goal="muscle_gain"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["fitness_goal"] == "muscle_gain"

    def test_updates_existing_profile(self, authed_client, db, sample_user, sample_profile):
        resp = authed_client.put(ME_URL, json={"fitness_goal": "endurance"})
        assert resp.status_code == 200
        assert resp.json()["fitness_goal"] == "endurance"

    def test_partial_update_does_not_overwrite_other_fields(
        self, authed_client, db, sample_user, sample_profile
    ):
        """Updating fitness_goal should not clear experience_level."""
        authed_client.put(ME_URL, json={"fitness_goal": "flexibility"})
        db.refresh(sample_profile)
        assert sample_profile.experience_level == "beginner"

    def test_update_numeric_fields(self, authed_client, db, sample_user):
        resp = authed_client.put(ME_URL, json={"current_weight": 75.5, "height": 180.0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["current_weight"] == 75.5
        assert data["height"] == 180.0

    def test_update_returns_profile_with_user_id(self, authed_client, db, sample_user):
        resp = authed_client.put(ME_URL, json=_update_payload())
        assert resp.json()["user_id"] == str(sample_user.id)

    def test_empty_update_body_returns_200(self, authed_client, sample_profile):
        """Empty dict still returns the (existing) profile."""
        resp = authed_client.put(ME_URL, json={})
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/profile/{user_id}
# ---------------------------------------------------------------------------

class TestGetUserProfile:
    def test_returns_profile_by_user_id(self, client, db, sample_user, sample_profile):
        resp = client.get(_user_url(sample_user.id))
        assert resp.status_code == 200
        assert resp.json()["user_id"] == str(sample_user.id)

    def test_returns_404_for_nonexistent_user(self, client):
        resp = client.get(_user_url(uuid.uuid4()))
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_public_endpoint_requires_no_auth(self, client, db, sample_user, sample_profile):
        """This endpoint has no auth dependency; no token needed."""
        resp = client.get(_user_url(sample_user.id))
        assert resp.status_code == 200

    def test_invalid_uuid_returns_422(self, client):
        resp = client.get(_user_url("not-a-uuid"))
        assert resp.status_code == 422

    def test_response_has_expected_fields(self, client, db, sample_user, sample_profile):
        resp = client.get(_user_url(sample_user.id))
        data = resp.json()
        for field in ("id", "user_id", "fitness_goal"):
            assert field in data


# ---------------------------------------------------------------------------
# DELETE /api/profile/me
# ---------------------------------------------------------------------------

class TestDeleteProfile:
    def test_delete_profile_and_user_returns_200(self, authed_client, db, sample_user, sample_profile):
        resp = authed_client.delete(ME_URL)
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"].lower()

    def test_delete_removes_profile_from_db(self, authed_client, db, sample_user, sample_profile):
        profile_id = sample_profile.id
        authed_client.delete(ME_URL)
        profile = db.query(Profile).filter(Profile.id == profile_id).first()
        assert profile is None

    def test_delete_removes_user_from_db(self, authed_client, db, sample_user, sample_profile):
        user_id = sample_user.id
        authed_client.delete(ME_URL)
        user = db.query(User).filter(User.id == user_id).first()
        assert user is None

    def test_delete_user_without_profile_still_works(self, authed_client, db, sample_user):
        """User with no profile should still be deletable."""
        resp = authed_client.delete(ME_URL)
        assert resp.status_code == 200
        user = db.query(User).filter(User.id == sample_user.id).first()
        assert user is None

    def test_delete_does_not_affect_other_users(self, authed_client, db, sample_user, sample_profile):
        other_user = User(
            id=uuid.uuid4(),
            email="other@example.com",
            password_hash="hashed",
        )
        other_profile = Profile(
            id=uuid.uuid4(),
            user_id=other_user.id,
            fitness_goal="strength",
        )
        db.add(other_user)
        db.add(other_profile)
        db.commit()

        authed_client.delete(ME_URL)

        remaining_user = db.query(User).filter(User.id == other_user.id).first()
        assert remaining_user is not None
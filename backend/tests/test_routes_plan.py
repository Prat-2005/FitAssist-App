"""
Tests for backend/routes/plan.py

Covers the authenticated CRUD endpoints:
  - GET  /api/plan/current
  - GET  /api/plan/{plan_id}
  - PUT  /api/plan/{plan_id}
  - POST /api/plan/{plan_id}/start
  - POST /api/plan/{plan_id}/complete-workout
"""

import sys
import os
import uuid
from datetime import datetime

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Plan


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plan_url(path=""):
    return f"/api/plan{path}"


def _make_plan(db, user, **kwargs):
    """Create a plan in the DB and return it."""
    defaults = dict(
        id=uuid.uuid4(),
        user_id=user.id,
        name="Default Plan",
        goal="General Fitness",
        workout_schedule='{"day1": "push"}',
        is_active=False,
        is_completed=False,
        progress_percentage=0,
    )
    defaults.update(kwargs)
    plan = Plan(**defaults)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


# ---------------------------------------------------------------------------
# GET /api/plan/current
# ---------------------------------------------------------------------------

class TestGetCurrentPlan:
    def test_returns_active_plan(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user, is_active=True)
        resp = authed_client.get(_plan_url("/current"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Default Plan"
        assert data["is_active"] is True

    def test_returns_404_when_no_active_plan(self, authed_client, db, sample_user):
        # Ensure no active plan exists
        resp = authed_client.get(_plan_url("/current"))
        assert resp.status_code == 404
        assert "active plan" in resp.json()["detail"].lower()

    def test_returns_only_active_plan(self, authed_client, db, sample_user):
        _make_plan(db, sample_user, name="Inactive", is_active=False)
        active = _make_plan(db, sample_user, name="Active One", is_active=True)
        resp = authed_client.get(_plan_url("/current"))
        assert resp.status_code == 200
        assert resp.json()["name"] == "Active One"


# ---------------------------------------------------------------------------
# GET /api/plan/{plan_id}
# ---------------------------------------------------------------------------

class TestGetPlan:
    def test_returns_plan_by_id(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user)
        resp = authed_client.get(_plan_url(f"/{plan.id}"))
        assert resp.status_code == 200
        assert resp.json()["id"] == str(plan.id)

    def test_returns_404_for_nonexistent_plan(self, authed_client):
        resp = authed_client.get(_plan_url(f"/{uuid.uuid4()}"))
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    def test_returns_404_for_other_users_plan(self, authed_client, db):
        """User cannot access another user's plan."""
        other_user_id = uuid.uuid4()
        plan = Plan(
            id=uuid.uuid4(),
            user_id=other_user_id,
            name="Other Plan",
            goal="Weight Loss",
            workout_schedule="{}",
            is_active=False,
            is_completed=False,
            progress_percentage=0,
        )
        db.add(plan)
        db.commit()
        resp = authed_client.get(_plan_url(f"/{plan.id}"))
        assert resp.status_code == 404

    def test_response_contains_expected_fields(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user)
        resp = authed_client.get(_plan_url(f"/{plan.id}"))
        data = resp.json()
        for field in ("id", "user_id", "name", "goal", "is_active", "is_completed", "progress_percentage"):
            assert field in data

    def test_invalid_uuid_returns_422(self, authed_client):
        resp = authed_client.get(_plan_url("/not-a-uuid"))
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# PUT /api/plan/{plan_id}
# ---------------------------------------------------------------------------

class TestUpdatePlan:
    def test_update_plan_name(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user)
        resp = authed_client.put(_plan_url(f"/{plan.id}"), json={"name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Name"

    def test_update_plan_goal(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user)
        resp = authed_client.put(_plan_url(f"/{plan.id}"), json={"goal": "Muscle Gain"})
        assert resp.status_code == 200
        assert resp.json()["goal"] == "Muscle Gain"

    def test_update_progress_percentage(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user)
        resp = authed_client.put(_plan_url(f"/{plan.id}"), json={"progress_percentage": 50})
        assert resp.status_code == 200
        assert resp.json()["progress_percentage"] == 50

    def test_update_nonexistent_plan_returns_404(self, authed_client):
        resp = authed_client.put(_plan_url(f"/{uuid.uuid4()}"), json={"name": "X"})
        assert resp.status_code == 404

    def test_update_only_provided_fields(self, authed_client, db, sample_user):
        """Excluded-unset fields should not change."""
        plan = _make_plan(db, sample_user, name="Original")
        authed_client.put(_plan_url(f"/{plan.id}"), json={"goal": "Endurance"})
        db.refresh(plan)
        assert plan.name == "Original"

    def test_update_other_users_plan_returns_404(self, authed_client, db):
        other_plan = Plan(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            name="Other",
            goal="X",
            workout_schedule="{}",
            is_active=False,
            is_completed=False,
            progress_percentage=0,
        )
        db.add(other_plan)
        db.commit()
        resp = authed_client.put(_plan_url(f"/{other_plan.id}"), json={"name": "Hack"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/plan/{plan_id}/start
# ---------------------------------------------------------------------------

class TestStartPlan:
    def test_start_plan_sets_is_active(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user, is_active=False)
        resp = authed_client.post(_plan_url(f"/{plan.id}/start"))
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True

    def test_start_plan_sets_started_at(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user)
        resp = authed_client.post(_plan_url(f"/{plan.id}/start"))
        assert resp.status_code == 200
        assert resp.json()["started_at"] is not None

    def test_start_plan_deactivates_other_active_plans(self, authed_client, db, sample_user):
        old_active = _make_plan(db, sample_user, name="Old Active", is_active=True)
        new_plan = _make_plan(db, sample_user, name="New Plan", is_active=False)
        authed_client.post(_plan_url(f"/{new_plan.id}/start"))
        db.refresh(old_active)
        assert old_active.is_active is False

    def test_start_nonexistent_plan_returns_404(self, authed_client):
        resp = authed_client.post(_plan_url(f"/{uuid.uuid4()}/start"))
        assert resp.status_code == 404

    def test_start_already_started_plan_preserves_started_at(self, authed_client, db, sample_user):
        original_start = datetime(2025, 1, 1, 0, 0, 0)
        plan = _make_plan(db, sample_user, started_at=original_start)
        resp = authed_client.post(_plan_url(f"/{plan.id}/start"))
        assert resp.status_code == 200
        # started_at should NOT be overwritten since it's already set
        assert resp.json()["started_at"] is not None
        db.refresh(plan)
        assert plan.started_at == original_start

    def test_start_other_users_plan_returns_404(self, authed_client, db):
        plan = Plan(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            name="X",
            goal="X",
            workout_schedule="{}",
            is_active=False,
            is_completed=False,
            progress_percentage=0,
        )
        db.add(plan)
        db.commit()
        resp = authed_client.post(_plan_url(f"/{plan.id}/start"))
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/plan/{plan_id}/complete-workout
# ---------------------------------------------------------------------------

class TestCompleteWorkout:
    def test_increments_progress_by_10(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user, progress_percentage=0)
        resp = authed_client.post(_plan_url(f"/{plan.id}/complete-workout"))
        assert resp.status_code == 200
        assert resp.json()["progress_percentage"] == 10

    def test_progress_does_not_exceed_100(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user, progress_percentage=95)
        resp = authed_client.post(_plan_url(f"/{plan.id}/complete-workout"))
        assert resp.status_code == 200
        assert resp.json()["progress_percentage"] == 100

    def test_plan_marked_completed_at_100_percent(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user, progress_percentage=90)
        resp = authed_client.post(_plan_url(f"/{plan.id}/complete-workout"))
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_completed"] is True
        assert data["completed_at"] is not None
        assert data["is_active"] is False

    def test_plan_not_completed_below_100(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user, progress_percentage=0)
        resp = authed_client.post(_plan_url(f"/{plan.id}/complete-workout"))
        assert resp.status_code == 200
        assert resp.json()["is_completed"] is False

    def test_complete_workout_nonexistent_plan_returns_404(self, authed_client):
        resp = authed_client.post(_plan_url(f"/{uuid.uuid4()}/complete-workout"))
        assert resp.status_code == 404

    def test_complete_workout_other_users_plan_returns_404(self, authed_client, db):
        plan = Plan(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            name="X",
            goal="X",
            workout_schedule="{}",
            is_active=True,
            is_completed=False,
            progress_percentage=0,
        )
        db.add(plan)
        db.commit()
        resp = authed_client.post(_plan_url(f"/{plan.id}/complete-workout"))
        assert resp.status_code == 404

    def test_multiple_completions_accumulate(self, authed_client, db, sample_user):
        plan = _make_plan(db, sample_user, progress_percentage=0)
        authed_client.post(_plan_url(f"/{plan.id}/complete-workout"))
        authed_client.post(_plan_url(f"/{plan.id}/complete-workout"))
        resp = authed_client.post(_plan_url(f"/{plan.id}/complete-workout"))
        assert resp.json()["progress_percentage"] == 30

    def test_boundary_at_exactly_90_percent_completes(self, authed_client, db, sample_user):
        """At 90%, one more completion brings it to 100% and marks completed."""
        plan = _make_plan(db, sample_user, progress_percentage=90)
        resp = authed_client.post(_plan_url(f"/{plan.id}/complete-workout"))
        assert resp.json()["is_completed"] is True
        assert resp.json()["progress_percentage"] == 100
"""
Tests for backend/schemas/

Covers Pydantic validation for:
  - UserRegister, UserLogin
  - ProfileCreate, ProfileUpdate, ProfileResponse
  - PlanCreate, PlanUpdate, PlanResponse
"""

import sys
import os
import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.user import UserRegister, UserLogin
from schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse
from schemas.plan import PlanCreate, PlanUpdate, PlanResponse


# ---------------------------------------------------------------------------
# UserRegister
# ---------------------------------------------------------------------------

class TestUserRegister:
    def test_valid_data(self):
        schema = UserRegister(first_name="Alice", email="alice@example.com", password="Pass123!")
        assert schema.first_name == "Alice"
        assert schema.email == "alice@example.com"
        assert schema.password == "Pass123!"

    def test_missing_first_name_raises(self):
        with pytest.raises(ValidationError):
            UserRegister(email="a@b.com", password="Pass")

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError):
            UserRegister(first_name="A", password="Pass")

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            UserRegister(first_name="A", email="a@b.com")

    def test_empty_first_name_allowed(self):
        """Pydantic str allows empty strings unless constrained."""
        schema = UserRegister(first_name="", email="a@b.com", password="Pass")
        assert schema.first_name == ""

    def test_extra_fields_not_stored(self):
        """Extra fields should be ignored (Pydantic default)."""
        schema = UserRegister(first_name="A", email="a@b.com", password="P", extra_field="x")
        assert not hasattr(schema, "extra_field")

    def test_no_args_raises(self):
        with pytest.raises(ValidationError):
            UserRegister()


# ---------------------------------------------------------------------------
# UserLogin
# ---------------------------------------------------------------------------

class TestUserLogin:
    def test_valid_data(self):
        schema = UserLogin(email="a@b.com", password="Pass")
        assert schema.email == "a@b.com"
        assert schema.password == "Pass"

    def test_missing_email_raises(self):
        with pytest.raises(ValidationError):
            UserLogin(password="Pass")

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            UserLogin(email="a@b.com")

    def test_no_first_name_field(self):
        schema = UserLogin(email="a@b.com", password="P")
        assert not hasattr(schema, "first_name")


# ---------------------------------------------------------------------------
# ProfileCreate / ProfileUpdate
# ---------------------------------------------------------------------------

class TestProfileCreate:
    def test_all_fields_optional(self):
        """ProfileCreate has only optional fields."""
        schema = ProfileCreate()
        assert schema.fitness_goal is None
        assert schema.experience_level is None

    def test_partial_data_accepted(self):
        schema = ProfileCreate(fitness_goal="weight_loss", experience_level="beginner")
        assert schema.fitness_goal == "weight_loss"

    def test_numeric_fields(self):
        schema = ProfileCreate(target_weight=70.5, current_weight=80.0, height=175.0,
                               body_fat_percentage=20.0)
        assert schema.target_weight == 70.5
        assert schema.height == 175.0

    def test_text_fields(self):
        schema = ProfileCreate(
            preferred_workouts='["running", "cycling"]',
            equipment_available='["dumbbells"]',
            medical_conditions="none",
            injuries="left knee"
        )
        assert schema.preferred_workouts == '["running", "cycling"]'


class TestProfileUpdate:
    def test_empty_update_allowed(self):
        schema = ProfileUpdate()
        assert schema.fitness_goal is None

    def test_partial_update(self):
        schema = ProfileUpdate(fitness_goal="endurance")
        assert schema.fitness_goal == "endurance"
        assert schema.experience_level is None


class TestProfileResponse:
    def test_valid_response(self):
        uid = uuid.uuid4()
        pid = uuid.uuid4()
        schema = ProfileResponse(id=pid, user_id=uid)
        assert schema.id == pid
        assert schema.user_id == uid

    def test_optional_fields_default_to_none(self):
        uid, pid = uuid.uuid4(), uuid.uuid4()
        schema = ProfileResponse(id=pid, user_id=uid)
        assert schema.fitness_goal is None
        assert schema.target_weight is None

    def test_missing_id_raises(self):
        with pytest.raises(ValidationError):
            ProfileResponse(user_id=uuid.uuid4())

    def test_missing_user_id_raises(self):
        with pytest.raises(ValidationError):
            ProfileResponse(id=uuid.uuid4())

    def test_from_attributes_config(self):
        assert ProfileResponse.model_config.get("from_attributes") is True


# ---------------------------------------------------------------------------
# PlanCreate
# ---------------------------------------------------------------------------

class TestPlanCreate:
    def test_valid_plan(self):
        schema = PlanCreate(
            name="My Plan",
            goal="General Fitness",
            workout_schedule='{"day1": "push"}'
        )
        assert schema.name == "My Plan"
        assert schema.goal == "General Fitness"

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError):
            PlanCreate(goal="X", workout_schedule="{}")

    def test_missing_goal_raises(self):
        with pytest.raises(ValidationError):
            PlanCreate(name="Plan", workout_schedule="{}")

    def test_missing_workout_schedule_raises(self):
        with pytest.raises(ValidationError):
            PlanCreate(name="Plan", goal="X")

    def test_optional_fields_default_none(self):
        schema = PlanCreate(name="P", goal="G", workout_schedule="{}")
        assert schema.description is None
        assert schema.duration_days is None
        assert schema.nutrition_guidelines is None
        assert schema.ai_model_used is None

    def test_all_fields_provided(self):
        schema = PlanCreate(
            name="Full Plan",
            goal="Muscle Gain",
            workout_schedule='{"day1": "legs"}',
            description="Desc",
            duration_days=30,
            nutrition_guidelines='{"calories": 2500}',
            ai_model_used="gemini"
        )
        assert schema.duration_days == 30
        assert schema.ai_model_used == "gemini"


# ---------------------------------------------------------------------------
# PlanUpdate
# ---------------------------------------------------------------------------

class TestPlanUpdate:
    def test_all_fields_optional(self):
        schema = PlanUpdate()
        assert schema.name is None
        assert schema.goal is None
        assert schema.is_active is None

    def test_partial_update(self):
        schema = PlanUpdate(name="Updated")
        assert schema.name == "Updated"
        assert schema.goal is None

    def test_boolean_fields(self):
        schema = PlanUpdate(is_active=True, is_completed=False)
        assert schema.is_active is True
        assert schema.is_completed is False

    def test_progress_percentage(self):
        schema = PlanUpdate(progress_percentage=75)
        assert schema.progress_percentage == 75

    def test_model_dump_excludes_unset(self):
        schema = PlanUpdate(name="New Name")
        dumped = schema.model_dump(exclude_unset=True)
        assert "name" in dumped
        assert "goal" not in dumped


# ---------------------------------------------------------------------------
# PlanResponse
# ---------------------------------------------------------------------------

class TestPlanResponse:
    def _make_response(self, **kwargs):
        defaults = dict(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            name="Plan",
            goal="General Fitness",
            workout_schedule="{}",
            is_active=False,
            is_completed=False,
            progress_percentage=0,
            created_at=datetime.utcnow(),
        )
        defaults.update(kwargs)
        return PlanResponse(**defaults)

    def test_valid_response(self):
        resp = self._make_response()
        assert resp.is_active is False
        assert resp.progress_percentage == 0

    def test_started_at_and_completed_at_default_none(self):
        resp = self._make_response()
        assert resp.started_at is None
        assert resp.completed_at is None

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            PlanResponse(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                # missing name, goal, workout_schedule, is_active, is_completed, etc.
            )

    def test_from_attributes_config(self):
        assert PlanResponse.model_config.get("from_attributes") is True

    def test_plan_response_with_all_fields(self):
        now = datetime.utcnow()
        resp = self._make_response(
            is_active=True,
            is_completed=False,
            progress_percentage=50,
            started_at=now,
            description="Some desc",
            duration_days=7,
        )
        assert resp.is_active is True
        assert resp.progress_percentage == 50
        assert resp.started_at == now
        assert resp.duration_days == 7

    def test_uuid_fields_are_uuids(self):
        resp = self._make_response()
        assert isinstance(resp.id, uuid.UUID)
        assert isinstance(resp.user_id, uuid.UUID)

    def test_completed_plan_fields(self):
        now = datetime.utcnow()
        resp = self._make_response(
            is_completed=True,
            completed_at=now,
            is_active=False,
            progress_percentage=100
        )
        assert resp.is_completed is True
        assert resp.completed_at == now
        assert resp.progress_percentage == 100
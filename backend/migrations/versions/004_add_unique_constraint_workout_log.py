"""Add unique constraint on WorkoutLog (user_id, plan_id, day_number, week_number, year)

Revision ID: 004
Revises: 003
Create Date: 2026-04-05 11:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add unique constraint on (user_id, plan_id, day_number, week_number, year) to workout_logs table"""
    op.create_unique_constraint(
        'uq_workout_log_user_plan_day_week_year',
        'workout_logs',
        ['user_id', 'plan_id', 'day_number', 'week_number', 'year']
    )


def downgrade() -> None:
    """Remove unique constraint from workout_logs table"""
    op.drop_constraint(
        'uq_workout_log_user_plan_day_week_year',
        'workout_logs',
        type_='unique'
    )

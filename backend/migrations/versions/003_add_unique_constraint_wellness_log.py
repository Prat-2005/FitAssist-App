"""Add unique constraint on WellnessLog (user_id, date)

Revision ID: 003
Revises: 002
Create Date: 2026-04-05 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add unique constraint on (user_id, date) to wellness_logs table"""
    op.create_unique_constraint(
        'uq_wellness_log_user_date',
        'wellness_logs',
        ['user_id', 'date']
    )


def downgrade() -> None:
    """Remove unique constraint from wellness_logs table"""
    op.drop_constraint(
        'uq_wellness_log_user_date',
        'wellness_logs',
        type_='unique'
    )

"""Add days_per_week and duration_minutes to Profile

Revision ID: 001
Revises: 
Create Date: 2026-04-05 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add new columns to profiles table"""
    op.add_column('profiles', sa.Column('days_per_week', sa.Integer(), nullable=True))
    op.add_column('profiles', sa.Column('duration_minutes', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Drop columns from profiles table"""
    op.drop_column('profiles', 'duration_minutes')
    op.drop_column('profiles', 'days_per_week')

"""Add ON DELETE CASCADE to WorkoutLog.plan_id foreign key

Revision ID: 002
Revises: 001
Create Date: 2026-04-05 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add CASCADE delete to WorkoutLog.plan_id foreign key"""
    # Drop the existing foreign key constraint
    op.drop_constraint('workout_logs_plan_id_fkey', 'workout_logs', type_='foreignkey')
    
    # Recreate the foreign key with ON DELETE CASCADE
    op.create_foreign_key(
        'workout_logs_plan_id_fkey',
        'workout_logs',
        'plans',
        ['plan_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Revert CASCADE delete from WorkoutLog.plan_id foreign key"""
    # Drop the CASCADE foreign key
    op.drop_constraint('workout_logs_plan_id_fkey', 'workout_logs', type_='foreignkey')
    
    # Recreate the foreign key without CASCADE
    op.create_foreign_key(
        'workout_logs_plan_id_fkey',
        'workout_logs',
        'plans',
        ['plan_id'],
        ['id']
    )

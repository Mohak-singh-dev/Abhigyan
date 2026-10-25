"""complaint timeline table

Revision ID: 003_complaint_timeline
Revises: 002_complaints
Create Date: 2026-10-25 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_complaint_timeline'
down_revision: Union[str, None] = '002_complaints'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'complaint_timelines',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('complaint_id', sa.String(length=64), nullable=False),
        sa.Column('label', sa.String(length=500), nullable=False),
        sa.Column('date', sa.String(length=50), nullable=False),
        sa.Column('by', sa.String(length=255), nullable=True),
        sa.Column('role', sa.String(length=50), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('user_id', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['complaint_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaint_timelines_id'), 'complaint_timelines', ['id'], unique=False)
    op.create_index(op.f('ix_complaint_timelines_complaint_id'), 'complaint_timelines', ['complaint_id'], unique=False)
    op.create_index(op.f('ix_complaint_timelines_user_id'), 'complaint_timelines', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_complaint_timelines_user_id'), table_name='complaint_timelines')
    op.drop_index(op.f('ix_complaint_timelines_complaint_id'), table_name='complaint_timelines')
    op.drop_index(op.f('ix_complaint_timelines_id'), table_name='complaint_timelines')
    op.drop_table('complaint_timelines')

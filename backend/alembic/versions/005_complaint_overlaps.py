"""complaint overlaps and overlap decision history tables

Revision ID: 005_complaint_overlaps
Revises: 004_user_password_hash
Create Date: 2026-10-26 20:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_complaint_overlaps'
down_revision: Union[str, None] = '005_ai_classification'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create complaint_overlaps
    op.create_table(
        'complaint_overlaps',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('complaint_a_id', sa.String(length=64), nullable=False),
        sa.Column('complaint_b_id', sa.String(length=64), nullable=False),
        sa.Column('similarity', sa.Integer(), nullable=False, server_default='85'),
        sa.Column('reasons', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='open'),
        sa.Column('decision_state', sa.String(length=50), nullable=True),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.String(length=255), nullable=True),
        sa.Column('reviewed_by_user_id', sa.String(length=64), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['complaint_a_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['complaint_b_id'], ['complaints.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewed_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaint_overlaps_id'), 'complaint_overlaps', ['id'], unique=False)
    op.create_index(op.f('ix_complaint_overlaps_complaint_a_id'), 'complaint_overlaps', ['complaint_a_id'], unique=False)
    op.create_index(op.f('ix_complaint_overlaps_complaint_b_id'), 'complaint_overlaps', ['complaint_b_id'], unique=False)
    op.create_index(op.f('ix_complaint_overlaps_status'), 'complaint_overlaps', ['status'], unique=False)
    op.create_index(op.f('ix_complaint_overlaps_reviewed_by_user_id'), 'complaint_overlaps', ['reviewed_by_user_id'], unique=False)

    # 2. Create complaint_overlap_history
    op.create_table(
        'complaint_overlap_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('overlap_id', sa.String(length=64), nullable=False),
        sa.Column('decision_state', sa.String(length=50), nullable=False),
        sa.Column('justification', sa.Text(), nullable=True),
        sa.Column('actor_name', sa.String(length=255), nullable=True),
        sa.Column('actor_user_id', sa.String(length=64), nullable=True),
        sa.Column('actor_role', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['overlap_id'], ['complaint_overlaps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaint_overlap_history_id'), 'complaint_overlap_history', ['id'], unique=False)
    op.create_index(op.f('ix_complaint_overlap_history_overlap_id'), 'complaint_overlap_history', ['overlap_id'], unique=False)
    op.create_index(op.f('ix_complaint_overlap_history_actor_user_id'), 'complaint_overlap_history', ['actor_user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_complaint_overlap_history_actor_user_id'), table_name='complaint_overlap_history')
    op.drop_index(op.f('ix_complaint_overlap_history_overlap_id'), table_name='complaint_overlap_history')
    op.drop_index(op.f('ix_complaint_overlap_history_id'), table_name='complaint_overlap_history')
    op.drop_table('complaint_overlap_history')

    op.drop_index(op.f('ix_complaint_overlaps_reviewed_by_user_id'), table_name='complaint_overlaps')
    op.drop_index(op.f('ix_complaint_overlaps_status'), table_name='complaint_overlaps')
    op.drop_index(op.f('ix_complaint_overlaps_complaint_b_id'), table_name='complaint_overlaps')
    op.drop_index(op.f('ix_complaint_overlaps_complaint_a_id'), table_name='complaint_overlaps')
    op.drop_index(op.f('ix_complaint_overlaps_id'), table_name='complaint_overlaps')
    op.drop_table('complaint_overlaps')

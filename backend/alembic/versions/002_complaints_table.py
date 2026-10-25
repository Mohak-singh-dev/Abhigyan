"""complaints table

Revision ID: 002_complaints
Revises: 001_initial
Create Date: 2026-10-25 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_complaints'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'complaints',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('institution_id', sa.String(length=64), nullable=False),
        sa.Column('institution_permanent_id', sa.String(length=64), nullable=True),
        sa.Column('bureau', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=255), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='Medium'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Pending'),
        sa.Column('officer', sa.String(length=255), nullable=False),
        sa.Column('assigned_user_id', sa.String(length=64), nullable=True),
        sa.Column('date', sa.String(length=50), nullable=False),
        sa.Column('due', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('complainant_type', sa.String(length=50), nullable=True, server_default='General Public'),
        sa.Column('complainant_name', sa.String(length=255), nullable=True),
        sa.Column('complainant_email', sa.String(length=255), nullable=True),
        sa.Column('complainant_phone', sa.String(length=50), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('next_action', sa.String(length=255), nullable=True),
        sa.Column('last_action_date', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['assigned_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_complaints_id'), 'complaints', ['id'], unique=False)
    op.create_index(op.f('ix_complaints_institution_id'), 'complaints', ['institution_id'], unique=False)
    op.create_index(op.f('ix_complaints_institution_permanent_id'), 'complaints', ['institution_permanent_id'], unique=False)
    op.create_index(op.f('ix_complaints_bureau'), 'complaints', ['bureau'], unique=False)
    op.create_index(op.f('ix_complaints_category'), 'complaints', ['category'], unique=False)
    op.create_index(op.f('ix_complaints_priority'), 'complaints', ['priority'], unique=False)
    op.create_index(op.f('ix_complaints_status'), 'complaints', ['status'], unique=False)
    op.create_index(op.f('ix_complaints_assigned_user_id'), 'complaints', ['assigned_user_id'], unique=False)
    op.create_index(op.f('ix_complaints_title'), 'complaints', ['title'], unique=False)
    op.create_index(op.f('ix_complaints_complainant_email'), 'complaints', ['complainant_email'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_complaints_complainant_email'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_title'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_assigned_user_id'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_status'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_priority'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_category'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_bureau'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_institution_permanent_id'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_institution_id'), table_name='complaints')
    op.drop_index(op.f('ix_complaints_id'), table_name='complaints')
    op.drop_table('complaints')

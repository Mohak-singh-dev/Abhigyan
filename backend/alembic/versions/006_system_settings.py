"""system settings table for persistent threshold and SLA configuration

Revision ID: 006_system_settings
Revises: 005_complaint_overlaps
Create Date: 2026-10-26 22:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_system_settings'
down_revision: Union[str, None] = '005_complaint_overlaps'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'system_settings',
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('similarity_threshold', sa.Integer(), nullable=False, server_default='75'),
        sa.Column('sla_critical', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('sla_high', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('sla_medium', sa.Integer(), nullable=False, server_default='14'),
        sa.Column('auto_escalate', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('email_alerts', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by_user_id', sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(['updated_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('key')
    )
    op.create_index(op.f('ix_system_settings_key'), 'system_settings', ['key'], unique=False)
    op.create_index(op.f('ix_system_settings_updated_by_user_id'), 'system_settings', ['updated_by_user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_system_settings_updated_by_user_id'), table_name='system_settings')
    op.drop_index(op.f('ix_system_settings_key'), table_name='system_settings')
    op.drop_table('system_settings')

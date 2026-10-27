"""add complainant_user_id to complaints table and backfill existing records

Revision ID: 007_add_complainant_user_id
Revises: 006_system_settings
Create Date: 2026-10-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '007_add_complainant_user_id'
down_revision: Union[str, None] = '006_system_settings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add complainant_user_id column to complaints table
    op.add_column('complaints', sa.Column('complainant_user_id', sa.String(length=64), nullable=True))
    op.create_foreign_key(
        'fk_complaints_complainant_user_id_users',
        'complaints',
        'users',
        ['complainant_user_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(op.f('ix_complaints_complainant_user_id'), 'complaints', ['complainant_user_id'], unique=False)

    # 2. Backfill existing records safely where complainant_email matches users.email
    op.execute("""
        UPDATE complaints c
        SET complainant_user_id = u.id
        FROM users u
        WHERE c.complainant_user_id IS NULL
          AND c.complainant_email IS NOT NULL
          AND LOWER(TRIM(c.complainant_email)) = LOWER(TRIM(u.email))
    """)


def downgrade() -> None:
    op.drop_constraint('fk_complaints_complainant_user_id_users', 'complaints', type_='foreignkey')
    op.drop_index(op.f('ix_complaints_complainant_user_id'), table_name='complaints')
    op.drop_column('complaints', 'complainant_user_id')

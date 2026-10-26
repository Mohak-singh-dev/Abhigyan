"""add ai classification columns to complaints table

Revision ID: 005_ai_classification
Revises: 004_user_password_hash
Create Date: 2026-10-27 00:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_ai_classification'
down_revision: Union[str, None] = '004_user_password_hash'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('complaints', sa.Column('ai_predicted_category', sa.String(length=255), nullable=True))
    op.add_column('complaints', sa.Column('ai_predicted_bureau', sa.String(length=50), nullable=True))
    op.add_column('complaints', sa.Column('ai_predicted_priority', sa.String(length=50), nullable=True))
    op.add_column('complaints', sa.Column('ai_confidence', sa.Float(), nullable=True))
    op.add_column('complaints', sa.Column('ai_needs_manual_review', sa.Boolean(), nullable=True, server_default=sa.text('false')))
    op.add_column('complaints', sa.Column('ai_model_version', sa.String(length=50), nullable=True))
    op.add_column('complaints', sa.Column('ai_classification_run', sa.Boolean(), nullable=True, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('complaints', 'ai_classification_run')
    op.drop_column('complaints', 'ai_model_version')
    op.drop_column('complaints', 'ai_needs_manual_review')
    op.drop_column('complaints', 'ai_confidence')
    op.drop_column('complaints', 'ai_predicted_priority')
    op.drop_column('complaints', 'ai_predicted_bureau')
    op.drop_column('complaints', 'ai_predicted_category')

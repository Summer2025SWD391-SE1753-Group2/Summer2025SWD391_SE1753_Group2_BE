"""Add is_active field to groups table

Revision ID: e0bcaa378ad2
Revises: add_chat_group_features
Create Date: 2025-07-05 14:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0bcaa378ad2'
down_revision: Union[str, None] = 'add_chat_group_features'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add is_active column to groups table
    op.add_column('groups', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove is_active column from groups table
    op.drop_column('groups', 'is_active')

"""update_timestamp_mixin

Revision ID: 23c8715d3cc9
Revises: 74355f4a8286
Create Date: 2025-06-03 15:51:01.911402

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23c8715d3cc9'
down_revision: Union[str, None] = '74355f4a8286'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

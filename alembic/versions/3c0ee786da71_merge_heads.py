"""merge heads

Revision ID: 3c0ee786da71
Revises: 20250217_comment, e0f42299693d
Create Date: 2025-06-12 19:54:18.669784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c0ee786da71'
down_revision: Union[str, None] = ('20250217_comment', 'e0f42299693d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

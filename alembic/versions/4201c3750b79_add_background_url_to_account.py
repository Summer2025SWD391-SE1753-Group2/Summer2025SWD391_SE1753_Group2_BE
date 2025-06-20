"""add_background_url_to_account

Revision ID: 4201c3750b79
Revises: add_friend
Create Date: 2025-06-20 18:25:18.902466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4201c3750b79'
down_revision: Union[str, None] = 'add_friend'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

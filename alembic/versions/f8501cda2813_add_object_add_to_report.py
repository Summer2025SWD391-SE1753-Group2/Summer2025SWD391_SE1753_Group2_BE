"""add object_add to report

Revision ID: f8501cda2813
Revises: 8e3a1ea1fa70
Create Date: 2025-07-16 22:06:02.342417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f8501cda2813'
down_revision: Union[str, None] = '8e3a1ea1fa70'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('report')]
    with op.batch_alter_table('report') as batch_op:
        if 'object_add' not in columns:
            batch_op.add_column(sa.Column('object_add', sa.Text(), nullable=True))
        if 'unit' not in columns:
            batch_op.add_column(sa.Column('unit', sa.String(255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Xóa cột object_add và unit khỏi bảng report khi downgrade
    with op.batch_alter_table('report') as batch_op:
        batch_op.drop_column('object_add')
        batch_op.drop_column('unit')

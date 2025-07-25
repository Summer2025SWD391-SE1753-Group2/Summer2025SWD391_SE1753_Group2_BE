"""drop unit table

Revision ID: 2cb1e521a985
Revises: 9328423dcfed
Create Date: 2025-07-02 17:44:13.803641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2cb1e521a985'
down_revision: Union[str, None] = '9328423dcfed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    constraints = [fk['name'] for fk in inspector.get_foreign_keys('post_material')]
    if 'post_material_unit_fkey' in constraints:
        op.drop_constraint('post_material_unit_fkey', 'post_material', type_='foreignkey')
    # op.drop_table('unit')  # Đã comment để không xóa bảng unit


def downgrade() -> None:
    """Downgrade schema."""
    # Nếu muốn rollback, cần tạo lại bảng unit và foreign key, nhưng thường không cần cho migration drop table

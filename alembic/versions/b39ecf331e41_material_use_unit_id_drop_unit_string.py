"""material use unit_id, drop unit string

Revision ID: b39ecf331e41
Revises: 2cb1e521a985
Create Date: 2025-07-02 17:57:41.425718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b39ecf331e41'
down_revision: Union[str, None] = '2cb1e521a985'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('material', sa.Column('unit_id', sa.UUID(), nullable=True))
    # Cập nhật dữ liệu unit_id dựa vào tên đơn vị cũ
    op.execute('''
        UPDATE material
        SET unit_id = u.unit_id
        FROM unit u
        WHERE material.unit = u.name
    ''')
    op.alter_column('material', 'unit_id', nullable=False)
    op.create_foreign_key(None, 'material', 'unit', ['unit_id'], ['unit_id'])
    op.drop_column('material', 'unit')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('material', sa.Column('unit', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'material', type_='foreignkey')
    op.create_foreign_key('material_unit_fkey', 'material', 'unit', ['unit'], ['name'])
    op.drop_column('material', 'unit_id')

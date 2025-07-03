"""add unit column to post_material

Revision ID: 9328423dcfed
Revises: 4201c3750b79
Create Date: 2025-07-02 17:36:53.746582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '9328423dcfed'
down_revision: Union[str, None] = '4201c3750b79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('post_material', sa.Column('unit', sa.String(length=50), nullable=True))
    # Không tạo foreign key tới unit nữa
    op.execute('''
        UPDATE post_material
        SET unit = material.unit
        FROM material
        WHERE post_material.material_id = material.material_id
    ''')
    op.alter_column('post_material', 'unit', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('post_material', 'unit')

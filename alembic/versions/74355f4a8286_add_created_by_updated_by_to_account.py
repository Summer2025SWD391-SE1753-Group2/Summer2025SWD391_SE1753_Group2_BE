"""add_created_by_updated_by_to_account

Revision ID: 74355f4a8286
Revises: 91522c504d72
Create Date: 2024-03-06 08:35:35.108730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '74355f4a8286'
down_revision: Union[str, None] = '91522c504d72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add created_by and updated_by columns to account table
    op.add_column('account', sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('account', sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True))
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_account_created_by',
        'account', 'account',
        ['created_by'], ['account_id']
    )
    op.create_foreign_key(
        'fk_account_updated_by',
        'account', 'account',
        ['updated_by'], ['account_id']
    )


def downgrade() -> None:
    # Remove foreign key constraints
    op.drop_constraint('fk_account_created_by', 'account', type_='foreignkey')
    op.drop_constraint('fk_account_updated_by', 'account', type_='foreignkey')
    
    # Remove columns
    op.drop_column('account', 'created_by')
    op.drop_column('account', 'updated_by')

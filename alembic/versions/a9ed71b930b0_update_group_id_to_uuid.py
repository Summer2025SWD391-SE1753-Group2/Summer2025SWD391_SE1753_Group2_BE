"""update group_id to uuid

Revision ID: a9ed71b930b0
Revises: a21d6e051761
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a9ed71b930b0'
down_revision: Union[str, None] = 'a21d6e051761'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing foreign key constraints
    op.drop_constraint('groups_topic_id_fkey', 'groups', type_='foreignkey')
    op.drop_constraint('groups_created_by_fkey', 'groups', type_='foreignkey')
    op.drop_constraint('groups_group_leader_fkey', 'groups', type_='foreignkey')

    # Create temporary column
    op.add_column('groups', sa.Column('group_id_new', postgresql.UUID(), nullable=True))
    
    # Convert existing group_id to UUID
    op.execute("UPDATE groups SET group_id_new = group_id::uuid")
    
    # Drop old column and rename new column
    op.drop_column('groups', 'group_id')
    op.alter_column('groups', 'group_id_new', new_column_name='group_id', nullable=False)
    
    # Add primary key constraint
    op.create_primary_key('groups_pkey', 'groups', ['group_id'])
    
    # Recreate foreign key constraints
    op.create_foreign_key('groups_topic_id_fkey', 'groups', 'topic', ['topic_id'], ['topic_id'])
    op.create_foreign_key('groups_created_by_fkey', 'groups', 'account', ['created_by'], ['account_id'])
    op.create_foreign_key('groups_group_leader_fkey', 'groups', 'account', ['group_leader'], ['account_id'])


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('groups_topic_id_fkey', 'groups', type_='foreignkey')
    op.drop_constraint('groups_created_by_fkey', 'groups', type_='foreignkey')
    op.drop_constraint('groups_group_leader_fkey', 'groups', type_='foreignkey')
    
    # Create temporary column
    op.add_column('groups', sa.Column('group_id_old', sa.String(), nullable=True))
    
    # Convert UUID back to string
    op.execute("UPDATE groups SET group_id_old = group_id::text")
    
    # Drop UUID column and rename string column
    op.drop_column('groups', 'group_id')
    op.alter_column('groups', 'group_id_old', new_column_name='group_id', nullable=False)
    
    # Add primary key constraint
    op.create_primary_key('groups_pkey', 'groups', ['group_id'])
    
    # Recreate foreign key constraints
    op.create_foreign_key('groups_topic_id_fkey', 'groups', 'topic', ['topic_id'], ['topic_id'])
    op.create_foreign_key('groups_created_by_fkey', 'groups', 'account', ['created_by'], ['account_id'])
    op.create_foreign_key('groups_group_leader_fkey', 'groups', 'account', ['group_leader'], ['account_id'])

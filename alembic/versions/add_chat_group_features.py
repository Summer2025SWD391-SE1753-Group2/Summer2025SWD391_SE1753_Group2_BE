# revision identifiers, used by Alembic.
revision = 'add_chat_group_features'
down_revision = 'add_friend_nickname'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    # Add new columns to groups table
    group_columns = [col['name'] for col in inspector.get_columns('groups')]
    if 'description' not in group_columns:
        op.add_column('groups', sa.Column('description', sa.Text(), nullable=True))
    if 'max_members' not in group_columns:
        op.add_column('groups', sa.Column('max_members', sa.Integer(), nullable=False, server_default='50'))
    if 'is_chat_group' not in group_columns:
        op.add_column('groups', sa.Column('is_chat_group', sa.Boolean(), nullable=False, server_default='false'))
    if 'updated_at' not in group_columns:
        op.add_column('groups', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # Add role column to group_members table
    gm_columns = [col['name'] for col in inspector.get_columns('group_members')]
    if 'role' not in gm_columns:
        op.add_column('group_members', sa.Column('role', sa.Enum('leader', 'moderator', 'member', name='groupmemberroleenum'), nullable=False, server_default='member'))

    # Create group_message table if not exists
    if 'group_message' not in inspector.get_table_names():
        op.create_table('group_message',
            sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('group_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('status', sa.Enum('sent', 'delivered', 'read', name='groupmessagestatusenum'), nullable=False),
            sa.Column('is_deleted', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['group_id'], ['groups.group_id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['sender_id'], ['account.account_id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('message_id')
        )
        op.create_index(op.f('ix_group_message_message_id'), 'group_message', ['message_id'], unique=False)
        op.create_index(op.f('ix_group_message_group_id'), 'group_message', ['group_id'], unique=False)
        op.create_index(op.f('ix_group_message_sender_id'), 'group_message', ['sender_id'], unique=False)

def downgrade():
    # Drop group_message table
    op.drop_index(op.f('ix_group_message_sender_id'), table_name='group_message')
    op.drop_index(op.f('ix_group_message_group_id'), table_name='group_message')
    op.drop_index(op.f('ix_group_message_message_id'), table_name='group_message')
    op.drop_table('group_message')
    
    # Drop columns from group_members
    op.drop_column('group_members', 'role')
    
    # Drop columns from groups
    op.drop_column('groups', 'updated_at')
    op.drop_column('groups', 'is_chat_group')
    op.drop_column('groups', 'max_members')
    op.drop_column('groups', 'description') 
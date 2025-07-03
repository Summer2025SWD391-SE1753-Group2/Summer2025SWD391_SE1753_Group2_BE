"""Create message table migration"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'create_message_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create message_status_enum
    op.execute("""
        CREATE TYPE messagestatusenum AS ENUM ('sent', 'delivered', 'read')
    """)
    
    # Create message table
    op.create_table('message',
        sa.Column('message_id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('receiver_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('sent', 'delivered', 'read', name='messagestatusenum'), nullable=False, default='sent'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['sender_id'], ['account.account_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['receiver_id'], ['account.account_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('message_id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_message_message_id'), 'message', ['message_id'], unique=False)
    op.create_index(op.f('ix_message_sender_id'), 'message', ['sender_id'], unique=False)
    op.create_index(op.f('ix_message_receiver_id'), 'message', ['receiver_id'], unique=False)
    op.create_index('ix_message_sender_receiver', 'message', ['sender_id', 'receiver_id'], unique=False)
    op.create_index('ix_message_created_at', 'message', ['created_at'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index('ix_message_created_at', table_name='message')
    op.drop_index('ix_message_sender_receiver', table_name='message')
    op.drop_index(op.f('ix_message_receiver_id'), table_name='message')
    op.drop_index(op.f('ix_message_sender_id'), table_name='message')
    op.drop_index(op.f('ix_message_message_id'), table_name='message')
    
    # Drop table
    op.drop_table('message')
    
    # Drop enum
    op.execute("DROP TYPE messagestatusenum") 
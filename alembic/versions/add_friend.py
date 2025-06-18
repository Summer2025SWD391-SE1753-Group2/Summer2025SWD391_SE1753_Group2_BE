"""add friend table

Revision ID: add_friend
Revises: 221e3fe9f6c5
Create Date: 2025-06-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_friend'
down_revision = '221e3fe9f6c5'
branch_labels = None
depends_on = None

def upgrade():
    # Create friend table using existing enum type
    op.create_table('friend',
        sa.Column('sender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('receiver_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'accepted', 'rejected', 
                                          name='friendstatusenum', 
                                          create_type=False), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['receiver_id'], ['account.account_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['account.account_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('sender_id', 'receiver_id')
    )

def downgrade():
    op.drop_table('friend')
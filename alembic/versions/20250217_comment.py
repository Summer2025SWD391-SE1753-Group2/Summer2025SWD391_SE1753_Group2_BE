"""create comments table

Revision ID: 20250217_comment
Revises: 036299d8bc7f
Create Date: 2024-02-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision: str = '20250217_comment'
down_revision: Union[str, None] = '036299d8bc7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create comments table
    op.create_table(
        'comments',
        sa.Column('comment_id', postgresql.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('post_id', postgresql.UUID(), nullable=False),
        sa.Column('account_id', postgresql.UUID(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('parent_comment_id', postgresql.UUID(), nullable=True),
        sa.Column('status', sa.Enum('active', 'reported', 'deleted', name='commentstatusenum'), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.ForeignKeyConstraint(['account_id'], ['account.account_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_comment_id'], ['comments.comment_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['post_id'], ['post.post_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('comment_id')
    )
    op.create_index(op.f('ix_comments_comment_id'), 'comments', ['comment_id'], unique=False)

def downgrade() -> None:
    # Drop comments table
    op.drop_index(op.f('ix_comments_comment_id'), table_name='comments')
    op.drop_table('comments') 
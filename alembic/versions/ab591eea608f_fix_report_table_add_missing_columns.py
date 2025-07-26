"""fix_report_table_add_missing_columns

Revision ID: ab591eea608f
Revises: 866c829ce0f0
Create Date: 2025-07-26 10:32:43.588551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ab591eea608f'
down_revision: Union[str, None] = '866c829ce0f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum types if they don't exist
    op.execute("DO $$ BEGIN CREATE TYPE reporttypeenum AS ENUM ('report_material', 'report_tag', 'report_topic', 'report_post', 'report_other'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE reportstatusenum AS ENUM ('pending', 'approve', 'reject'); EXCEPTION WHEN duplicate_object THEN null; END $$;")
    
    # Add missing columns to report table
    with op.batch_alter_table('report') as batch_op:
        # Add type column
        batch_op.add_column(sa.Column('type', sa.Enum('report_material', 'report_tag', 'report_topic', 'report_post', 'report_other', name='reporttypeenum'), nullable=True))
        
        # Add status column with default value
        batch_op.add_column(sa.Column('status', sa.Enum('pending', 'approve', 'reject', name='reportstatusenum'), nullable=True, server_default='pending'))
    
    # Update existing rows to have a default type and status
    op.execute("UPDATE report SET type = 'report_other' WHERE type IS NULL")
    op.execute("UPDATE report SET status = 'pending' WHERE status IS NULL")
    
    # Make columns not nullable after setting default values
    with op.batch_alter_table('report') as batch_op:
        batch_op.alter_column('type', nullable=False)
        batch_op.alter_column('status', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove columns from report table
    with op.batch_alter_table('report') as batch_op:
        batch_op.drop_column('status')
        batch_op.drop_column('type')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS reportstatusenum")
    op.execute("DROP TYPE IF EXISTS reporttypeenum")

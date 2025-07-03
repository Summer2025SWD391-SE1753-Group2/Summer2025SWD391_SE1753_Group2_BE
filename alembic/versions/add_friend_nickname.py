# revision identifiers, used by Alembic.
revision = 'add_friend_nickname'
down_revision = 'b39ecf331e41'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('friend', sa.Column('sender_nickname', sa.String(length=100), nullable=True))
    op.add_column('friend', sa.Column('receiver_nickname', sa.String(length=100), nullable=True))

def downgrade():
    op.drop_column('friend', 'sender_nickname')
    op.drop_column('friend', 'receiver_nickname') 
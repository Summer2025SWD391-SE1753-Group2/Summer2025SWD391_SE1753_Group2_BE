from sqlalchemy import Table, Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
from datetime import datetime, timezone

favourite_posts = Table(
    "favourite_posts",
    Base.metadata,
    Column("favourite_id", UUID(as_uuid=True), ForeignKey("favourites.favourite_id", ondelete="CASCADE"), primary_key=True),
    Column("post_id", UUID(as_uuid=True), ForeignKey("post.post_id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
) 
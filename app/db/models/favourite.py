from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base
import uuid

class Favourite(Base):
    __tablename__ = "favourites"

    favourite_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id", ondelete="CASCADE"), nullable=False)
    favourite_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    account = relationship("Account", back_populates="favourites")
    posts = relationship("Post", secondary="favourite_posts", back_populates="favourites") 
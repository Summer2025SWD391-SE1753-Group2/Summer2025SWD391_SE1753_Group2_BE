from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import event
import uuid

class CommentStatusEnum(str, enum.Enum):
    active = "active"
    reported = "reported"
    deleted = "deleted"

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    post_id = Column(UUID, ForeignKey("post.post_id", ondelete="CASCADE"), nullable=False)
    account_id = Column(UUID, ForeignKey("account.account_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    parent_comment_id = Column(UUID, ForeignKey("comments.comment_id", ondelete="CASCADE"), nullable=True)
    status = Column(Enum(CommentStatusEnum), default=CommentStatusEnum.active)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    level = Column(Integer, default=1)  # Track nesting level

    # Relationships
    post = relationship("Post", back_populates="comments")
    account = relationship("Account", back_populates="comments")
    parent = relationship("Comment", remote_side=[comment_id], backref="replies") 
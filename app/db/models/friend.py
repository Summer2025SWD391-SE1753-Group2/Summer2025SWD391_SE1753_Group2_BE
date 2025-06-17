from sqlalchemy import Column, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum
from datetime import datetime, timezone

class FriendStatusEnum(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Friend(Base):
    __tablename__ = "friend"

    sender_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id", ondelete="CASCADE"), primary_key=True)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id", ondelete="CASCADE"), primary_key=True)
    status = Column(Enum(FriendStatusEnum), default=FriendStatusEnum.pending)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    sender = relationship("Account", foreign_keys=[sender_id], backref="friend_requests_sent")
    receiver = relationship("Account", foreign_keys=[receiver_id], backref="friend_requests_received")
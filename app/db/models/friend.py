from sqlalchemy import Column, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime, timezone
from app.db.base_class import Base

class FriendStatusEnum(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Friend(Base):
    __tablename__ = "friend"

    sender_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id", ondelete="CASCADE"), primary_key=True)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id", ondelete="CASCADE"), primary_key=True)
    status = Column(Enum(FriendStatusEnum), nullable=False, default=FriendStatusEnum.pending)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    sender = relationship("Account", foreign_keys=[sender_id], back_populates="friends_sent")
    receiver = relationship("Account", foreign_keys=[receiver_id], back_populates="friends_received")
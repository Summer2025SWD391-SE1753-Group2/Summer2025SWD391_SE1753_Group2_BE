from sqlalchemy import Column, ForeignKey, DateTime, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime, timezone
from app.db.base_class import Base

class GroupMessageStatusEnum(str, enum.Enum):
    sent = "sent"
    delivered = "delivered"
    read = "read"

class GroupMessage(Base):
    __tablename__ = "group_message"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.group_id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    status = Column(Enum(GroupMessageStatusEnum), default=GroupMessageStatusEnum.sent, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    group = relationship("Group", back_populates="messages")
    sender = relationship("Account", back_populates="group_messages_sent") 
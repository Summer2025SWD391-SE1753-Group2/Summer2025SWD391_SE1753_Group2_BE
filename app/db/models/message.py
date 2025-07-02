from sqlalchemy import Column, ForeignKey, DateTime, Text, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
import uuid
from datetime import datetime, timezone
from app.db.base_class import Base

class MessageStatusEnum(str, enum.Enum):
    sent = "sent"
    delivered = "delivered"
    read = "read"

class Message(Base):
    __tablename__ = "message"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    status = Column(Enum(MessageStatusEnum), default=MessageStatusEnum.sent, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    sender = relationship("Account", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("Account", foreign_keys=[receiver_id], back_populates="received_messages") 
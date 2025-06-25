from datetime import datetime, timezone
import enum
import uuid
from sqlalchemy import Column, String, Enum, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class FeedbackStatusEnum(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"

class FeedbackPriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    feedback_type_id = Column(UUID(as_uuid=True), ForeignKey("feedback_type.feedback_type_id"), nullable=False)
    priority = Column(Enum(FeedbackPriorityEnum), default=FeedbackPriorityEnum.medium)
    status = Column(Enum(FeedbackStatusEnum), default=FeedbackStatusEnum.pending)
    
    # Optional fields for additional context
    screenshot_url = Column(Text, nullable=True)
    browser_info = Column(String(200), nullable=True)
    device_info = Column(String(200), nullable=True)
    
    # Resolution fields
    resolution_note = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps and audit
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign keys
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    
    # Relationships
    creator = relationship("Account", foreign_keys=[created_by], back_populates="feedbacks_created")
    updater = relationship("Account", foreign_keys=[updated_by], back_populates="feedbacks_updated")
    resolver = relationship("Account", foreign_keys=[resolved_by], back_populates="feedbacks_resolved")
    feedback_type_rel = relationship("FeedbackType", back_populates="feedbacks") 
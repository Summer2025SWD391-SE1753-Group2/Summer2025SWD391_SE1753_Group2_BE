from datetime import datetime, timezone
import enum
import uuid
from sqlalchemy import Column, String, Enum, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class FeedbackTypeStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class FeedbackType(Base):
    __tablename__ = "feedback_type"

    feedback_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(100), nullable=True)  # Icon class or URL
    color = Column(String(7), nullable=True)   # Hex color code
    is_default = Column(Boolean, default=False)  # Default types cannot be deleted
    status = Column(Enum(FeedbackTypeStatusEnum), default=FeedbackTypeStatusEnum.active)
    sort_order = Column(String(10), default="0")  # For ordering in UI
    
    # Timestamps and audit
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Foreign keys
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    
    # Relationships
    creator = relationship("Account", foreign_keys=[created_by], back_populates="feedback_types_created")
    updater = relationship("Account", foreign_keys=[updated_by], back_populates="feedback_types_updated")
    feedbacks = relationship("Feedback", back_populates="feedback_type_rel") 
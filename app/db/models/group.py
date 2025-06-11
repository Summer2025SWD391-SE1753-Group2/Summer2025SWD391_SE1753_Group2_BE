from sqlalchemy import Column, String, DateTime, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid
from datetime import datetime, timezone

class Group(Base):
    __tablename__ = "groups"

    group_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topic.topic_id"), nullable=False)
    name = Column(String(255), nullable=False)
    group_leader = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    topic = relationship("Topic", back_populates="groups")
    creator = relationship("Account", foreign_keys=[created_by], back_populates="created_groups")
    leader = relationship("Account", foreign_keys=[group_leader], back_populates="led_groups")
    members = relationship("GroupMember", back_populates="group") 
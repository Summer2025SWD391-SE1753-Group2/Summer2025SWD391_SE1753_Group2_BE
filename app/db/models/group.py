from sqlalchemy import Column, String, DateTime, ForeignKey, UUID, Boolean, Text, Integer
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid
from datetime import datetime, timezone

class Group(Base):
    __tablename__ = "groups"

    group_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topic.topic_id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)  # Mô tả group
    group_leader = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=False)
    max_members = Column(Integer, default=50, nullable=False)  # Số thành viên tối đa
    is_chat_group = Column(Boolean, default=False, nullable=False)  # Đánh dấu là chat group
    is_active = Column(Boolean, default=True, nullable=False)  # Trạng thái hoạt động của group
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    topic = relationship("Topic", back_populates="groups")
    creator = relationship("Account", foreign_keys=[created_by], back_populates="created_groups")
    leader = relationship("Account", foreign_keys=[group_leader], back_populates="led_groups")
    members = relationship("GroupMember", back_populates="group")
    messages = relationship("GroupMessage", back_populates="group") 
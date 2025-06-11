from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Group(Base):
    __tablename__ = "groups"

    group_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topic.topic_id"))
    name = Column(String(255))
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"))
    group_leader = Column(UUID(as_uuid=True), ForeignKey("account.account_id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="groups")
    creator = relationship("Account", foreign_keys=[created_by], back_populates="created_groups")
    leader = relationship("Account", foreign_keys=[group_leader], back_populates="led_groups") 
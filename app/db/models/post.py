from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Text, Boolean, DateTime, Date
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone

import enum

class PostStatusEnum(str, enum.Enum):
    waiting = "waiting"
    approved = "approved"
    rejected = "rejected"
import uuid                         
from sqlalchemy.dialects.postgresql import UUID
class Post(Base):
    __tablename__ = "post"

    post_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(PostStatusEnum), default=PostStatusEnum.waiting)
    rejection_reason = Column(Text, nullable=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)

    # Quan hệ many-to-many
    tags = relationship("Tag", secondary="post_tag", back_populates="posts")
    # materials = relationship("Material", secondary="post_material", back_populates="posts")
    # topics = relationship("Topic", secondary="post_topic", back_populates="posts")
    # images = relationship("PostImage", back_populates="post")

    # Quan hệ one-to-many ngược với Account
    creator = relationship("Account", back_populates="posts_created", foreign_keys=[created_by])
    updater = relationship("Account", back_populates="posts_updated", foreign_keys=[updated_by])

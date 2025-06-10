from datetime import datetime, timezone
import enum
import uuid
from sqlalchemy import Column, String, Enum, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from .post_tag import post_tag
from .post_topic import post_topic
from app.db.models.post_material import PostMaterial
from app.db.models.material import Material
from app.db.models.topic import Topic
from app.db.models.postImage import PostImage
from app.db.models.tag import Tag

class PostStatusEnum(str, enum.Enum):
    waiting = "waiting"
    approved = "approved"
    rejected = "rejected"

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

    # Relationships
    tags = relationship(Tag, secondary=post_tag, back_populates="posts")
    topics = relationship("Topic", secondary=post_topic, back_populates="posts")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")
    post_materials = relationship("PostMaterial", back_populates="post", cascade="all, delete-orphan")
    
    # Account relationships
    creator = relationship("Account", back_populates="posts_created", foreign_keys=[created_by])
    updater = relationship("Account", back_populates="posts_updated", foreign_keys=[updated_by])
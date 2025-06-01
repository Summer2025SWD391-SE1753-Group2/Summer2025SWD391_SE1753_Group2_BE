import uuid
from sqlalchemy import Column, String ,DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from app.db.base_class import Base
from sqlalchemy import Enum
class TagStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
class Tag(Base):
    __tablename__ = "tag"

    tag_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    status = Column(Enum(TagStatusEnum), default=TagStatusEnum.active)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)

    # Quan hệ many-to-many với Post
    posts = relationship("Post", secondary="post_tag", back_populates="tags")

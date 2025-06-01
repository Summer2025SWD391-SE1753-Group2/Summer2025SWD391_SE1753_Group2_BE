import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base_class import Base
import enum

class MaterialStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class Material(Base):
    __tablename__ = "material"

    material_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), unique=True, nullable=False)
    status = Column(SQLEnum(MaterialStatusEnum), default=MaterialStatusEnum.active)
    image_url = Column(String(500), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)

    # Quan hệ many-to-many với Post
    posts = relationship("Post", secondary="post_material", back_populates="materials")

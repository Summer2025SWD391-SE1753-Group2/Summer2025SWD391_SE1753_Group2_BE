from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from app.db.base_class import Base
import enum
from sqlalchemy import Enum
import uuid
class UnitStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"
class Unit(Base):
    __tablename__ = "unit"
    unit_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)  # Changed from primary_key to unique
    description = Column(String(200), nullable=True)
    status = Column(Enum(UnitStatusEnum), default=UnitStatusEnum.active)
    
    # Add timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Add creator and updater references
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
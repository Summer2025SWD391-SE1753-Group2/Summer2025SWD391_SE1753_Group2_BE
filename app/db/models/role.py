from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
import enum
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
class RoleNameEnum(str, enum.Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"

class RoleStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class Role(Base):
    __tablename__ = "role"

    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(Enum(RoleNameEnum), nullable=False, unique=True)
    status = Column(Enum(RoleStatusEnum), default=RoleStatusEnum.active)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)

    # Chỉ định foreign_keys cụ thể
    accounts = relationship("Account", back_populates="role", foreign_keys="[Account.role_id]")


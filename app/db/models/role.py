from sqlalchemy import Column, Integer, String, Enum, DateTime
from app.db.base_class import Base
from datetime import datetime, timezone
import enum

class RoleNameEnum(str, enum.Enum):
    user_l1 = "user l1"
    user_l2 = "user l2"
    moderator = "moderator"
    admin = "admin"

class RoleStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class Role(Base):
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(Enum(RoleNameEnum), nullable=False)
    status = Column(Enum(RoleStatusEnum), default=RoleStatusEnum.active)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    created_by = Column(String(100))
    updated_by = Column(String(100))

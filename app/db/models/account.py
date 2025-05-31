from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Text, Boolean, DateTime, Date
from app.db.base_class import Base
from datetime import datetime, timezone

import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class AccountStatusEnum(str, enum.Enum):
    active = "active"
    banned = "banned"
    inactive = "inactive"

class Account(Base):
    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    role_id = Column(Integer, ForeignKey("role.role_id"))
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    email_verified = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True)
    phone_verified = Column(Boolean, default=False)
    full_name = Column(String(255))
    date_of_birth = Column(Date, nullable=True)  # Add this line
    avatar = Column(Text, nullable=True, server_default="")
    bio = Column(Text, nullable=True, server_default="")
    status = Column(Enum(AccountStatusEnum), default=AccountStatusEnum.active)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    created_by = Column(String(100))
    updated_by = Column(String(100))

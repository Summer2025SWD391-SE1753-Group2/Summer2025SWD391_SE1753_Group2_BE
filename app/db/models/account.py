from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Text, Boolean, DateTime, Date
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
from app.db.models.post import Post
from app.db.models.friend import Friend
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class AccountStatusEnum(str, enum.Enum):
    active = "active"
    banned = "banned"
    inactive = "inactive"

class Account(Base):
    __tablename__ = "account"

    account_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    role_id = Column(Integer, ForeignKey("role.role_id"))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    email_verified = Column(Boolean, default=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    phone_verified = Column(Boolean, default=False)
    full_name = Column(String(255))
    date_of_birth = Column(Date, nullable=True)
    avatar = Column(Text, nullable=True)
    background_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    status = Column(Enum(AccountStatusEnum), default=AccountStatusEnum.active)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=True)

    # Quan hệ
    role = relationship("Role", back_populates="accounts", foreign_keys=[role_id])

    # Liên kết Post mà account tạo hoặc cập nhật
    posts_created = relationship(
        "Post",
        back_populates="creator",
        foreign_keys=[Post.created_by]
    )
    posts_updated = relationship(
        "Post",
        back_populates="updater",
        foreign_keys=[Post.updated_by]
    )

    # Liên kết với Group
    created_groups = relationship("Group", foreign_keys="Group.created_by", back_populates="creator")
    led_groups = relationship("Group", foreign_keys="Group.group_leader", back_populates="leader")
    group_memberships = relationship("GroupMember", back_populates="account")

    # Liên kết với Comment
    comments = relationship("Comment", back_populates="account", cascade="all, delete-orphan")

    # Liên kết với Favourite
    favourites = relationship("Favourite", back_populates="account", cascade="all, delete-orphan")
    friends_sent = relationship(
        "Friend",
        primaryjoin="Account.account_id==Friend.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    
    friends_received = relationship(
        "Friend",
        primaryjoin="Account.account_id==Friend.receiver_id", 
        back_populates="receiver",
        cascade="all, delete-orphan"
    )
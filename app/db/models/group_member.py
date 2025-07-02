from sqlalchemy import Column, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

class GroupMemberRoleEnum(str, enum.Enum):
    leader = "leader"
    moderator = "moderator" 
    member = "member"

class GroupMember(Base):
    __tablename__ = "group_members"

    group_member_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.account_id"))
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.group_id"))
    role = Column(SQLEnum(GroupMemberRoleEnum), default=GroupMemberRoleEnum.member, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    account = relationship("Account", back_populates="group_memberships")
    group = relationship("Group", back_populates="members") 
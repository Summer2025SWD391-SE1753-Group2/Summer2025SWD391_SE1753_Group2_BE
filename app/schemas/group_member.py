from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.db.models.group_member import GroupMemberRoleEnum
from app.schemas.group import GroupMemberStatusEnum

class GroupMemberBase(BaseModel):
    account_id: UUID4
    group_id: UUID4
    status: Optional[GroupMemberStatusEnum] = GroupMemberStatusEnum.active

class GroupMemberCreate(GroupMemberBase):
    pass

class GroupMemberUpdate(BaseModel):
    account_id: Optional[UUID4] = None
    group_id: Optional[UUID4] = None
    status: Optional[GroupMemberStatusEnum] = None

class GroupMemberInDBBase(GroupMemberBase):
    group_member_id: UUID4
    role: GroupMemberRoleEnum
    status: GroupMemberStatusEnum
    joined_at: datetime

    class Config:
        from_attributes = True

class GroupMember(GroupMemberInDBBase):
    pass

class GroupMemberWithDetails(BaseModel):
    items: List[GroupMember]
    total: int
    skip: int
    limit: int

class MembershipStatusResponse(BaseModel):
    group_id: str
    is_member: bool
    role: Optional[GroupMemberRoleEnum] = None
    status: str  # 'active', 'inactive', 'left', 'removed', 'banned', 'no-join'
    is_active: bool
    joined_at: Optional[datetime] = None

class BatchMembershipResponse(BaseModel):
    memberships: List[MembershipStatusResponse]
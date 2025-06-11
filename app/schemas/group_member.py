from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List, Dict, Any

class GroupMemberBase(BaseModel):
    account_id: UUID4
    group_id: UUID4

class GroupMemberCreate(GroupMemberBase):
    pass

class GroupMemberUpdate(BaseModel):
    account_id: Optional[UUID4] = None
    group_id: Optional[UUID4] = None

class GroupMemberInDBBase(GroupMemberBase):
    group_member_id: UUID4
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
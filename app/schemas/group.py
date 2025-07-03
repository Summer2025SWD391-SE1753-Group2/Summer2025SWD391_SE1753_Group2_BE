from pydantic import BaseModel, UUID4, validator, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException, status
from uuid import UUID
from enum import Enum

class GroupMemberRoleEnum(str, Enum):
    leader = "leader"
    moderator = "moderator"
    member = "member"

class GroupBase(BaseModel):
    topic_id: UUID4
    name: str = Field(..., min_length=1, max_length=255, description="Group name")
    description: Optional[str] = Field(None, max_length=1000, description="Group description")
    max_members: int = Field(50, ge=1, le=50, description="Maximum number of members")

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip()

class GroupCreate(BaseModel):
    topic_id: UUID4
    name: str = Field(..., min_length=1, max_length=255, description="Group name")
    description: Optional[str] = Field(None, max_length=1000, description="Group description")
    max_members: int = Field(50, ge=1, le=50, description="Maximum number of members")

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip()

class GroupUpdate(BaseModel):
    topic_id: Optional[UUID4] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    max_members: Optional[int] = Field(None, ge=1, le=50)
    group_leader: Optional[UUID4] = None

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip() if v else v

class GroupInDBBase(GroupBase):
    group_id: UUID4
    created_by: UUID4
    created_at: datetime
    updated_at: datetime
    is_chat_group: bool

    class Config:
        from_attributes = True

class Group(GroupInDBBase):
    pass

class GroupSearchResponse(BaseModel):
    items: List[Group]
    total: int
    skip: int
    limit: int

class GroupOut(GroupBase):
    group_id: UUID
    topic_id: UUID
    group_leader: UUID
    created_by: UUID
    is_chat_group: bool
    created_at: datetime
    updated_at: datetime
    
    # Related info
    topic_name: Optional[str] = None
    leader_name: Optional[str] = None
    member_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True, json_encoders={
        datetime: lambda v: v.isoformat(),
        UUID: lambda v: str(v)
    })

class GroupMemberBase(BaseModel):
    role: GroupMemberRoleEnum = GroupMemberRoleEnum.member

class GroupMemberCreate(BaseModel):
    account_id: UUID = Field(..., description="Account ID to add to group")
    role: GroupMemberRoleEnum = GroupMemberRoleEnum.member

class GroupMemberOut(BaseModel):
    group_member_id: UUID
    account_id: UUID
    group_id: UUID
    role: GroupMemberRoleEnum
    joined_at: datetime
    
    # Related account info
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, json_encoders={
        datetime: lambda v: v.isoformat(),
        UUID: lambda v: str(v)
    })

class GroupList(BaseModel):
    groups: List[GroupOut]
    total: int
    skip: int
    limit: int

class GroupChatCreateTransaction(BaseModel):
    topic_id: UUID4
    name: str = Field(..., min_length=1, max_length=100, description="Group name")
    description: Optional[str] = Field(None, max_length=500, description="Group description")
    member_ids: List[UUID4] = Field(..., min_items=2, max_items=49, description="List of member account IDs (không bao gồm creator)")

class GroupChatTransactionOut(BaseModel):
    group: GroupOut
    members: List[GroupMemberOut] 
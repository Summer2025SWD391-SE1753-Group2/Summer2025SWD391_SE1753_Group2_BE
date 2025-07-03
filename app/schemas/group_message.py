from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class GroupMessageStatusEnum(str, Enum):
    sent = "sent"
    delivered = "delivered"
    read = "read"

class GroupMessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Message content")

class GroupMessageCreate(GroupMessageBase):
    group_id: UUID = Field(..., description="Group ID to send message to")

class GroupMessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    is_deleted: Optional[bool] = None

class GroupMessageOut(GroupMessageBase):
    message_id: UUID
    group_id: UUID
    sender_id: UUID
    status: GroupMessageStatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    
    # Related account information
    sender: "AccountSummary"

    model_config = ConfigDict(from_attributes=True, json_encoders={
        datetime: lambda v: v.isoformat(),
        UUID: lambda v: str(v)
    })

class GroupMessageList(BaseModel):
    messages: List[GroupMessageOut]
    total: int
    skip: int
    limit: int

# Import AccountSummary to avoid circular imports
from app.schemas.common import AccountSummary 
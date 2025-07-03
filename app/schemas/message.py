from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class MessageStatusEnum(str, Enum):
    sent = "sent"
    delivered = "delivered"
    read = "read"

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Message content")

class MessageCreate(MessageBase):
    receiver_id: UUID = Field(..., description="ID of the message recipient")

class MessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    is_deleted: Optional[bool] = None

class MessageOut(MessageBase):
    message_id: UUID
    sender_id: UUID
    receiver_id: UUID
    status: MessageStatusEnum
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    read_at: Optional[datetime] = None
    
    # Related account information
    sender: "AccountSummary"
    receiver: "AccountSummary"

    model_config = ConfigDict(from_attributes=True, json_encoders={
        datetime: lambda v: v.isoformat(),
        UUID: lambda v: str(v)
    })

class MessageList(BaseModel):
    messages: List[MessageOut]
    total: int
    skip: int
    limit: int

class ChatHistoryRequest(BaseModel):
    friend_id: UUID = Field(..., description="ID of the friend to get chat history with")
    skip: int = Field(0, ge=0, description="Number of messages to skip")
    limit: int = Field(50, ge=1, le=100, description="Number of messages to return")

# Import AccountSummary to avoid circular imports
from app.schemas.common import AccountSummary 
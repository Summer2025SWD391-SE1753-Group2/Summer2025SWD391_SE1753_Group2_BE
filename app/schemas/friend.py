from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from enum import Enum

class FriendStatusEnum(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class FriendRequest(BaseModel):
    receiver_id: UUID

class FriendResponse(BaseModel):
    sender_id: UUID
    receiver_id: UUID
    status: FriendStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
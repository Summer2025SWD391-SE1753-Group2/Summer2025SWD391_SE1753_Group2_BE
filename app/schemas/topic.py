from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class TopicStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"


class TopicBase(BaseModel):
    name: str = Field(..., max_length=150)
    status: Optional[TopicStatusEnum] = TopicStatusEnum.active


class TopicCreate(TopicBase):
    created_by: Optional[UUID] = None

class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    status: Optional[TopicStatusEnum] = None


class TopicOut(BaseModel):
    topic_id: UUID
    name: str
    status: TopicStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# Schema response phân trang
class TopicListResponse(BaseModel):
    topics: List[TopicOut]
    total: int
    skip: int
    limit: int
    has_more: bool
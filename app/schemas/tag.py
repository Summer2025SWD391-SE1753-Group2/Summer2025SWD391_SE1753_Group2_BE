from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class TagStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"


# Base dùng chung
class TagBase(BaseModel):
    name: str
    status: Optional[TagStatusEnum] = TagStatusEnum.active


# Schema khi tạo mới
class TagCreate(TagBase):
    pass


# Schema khi update
class TagUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[TagStatusEnum] = None


# Schema khi trả dữ liệu ra ngoài
class TagOut(TagBase):
    tag_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        orm_mode = True

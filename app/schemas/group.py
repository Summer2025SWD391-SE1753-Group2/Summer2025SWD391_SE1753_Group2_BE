from pydantic import BaseModel, UUID4, validator
from datetime import datetime
from typing import Optional, List
from fastapi import HTTPException, status

class GroupBase(BaseModel):
    topic_id: UUID4
    name: str
    group_leader: UUID4

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name must not be empty')
        return v.strip()

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    topic_id: Optional[UUID4] = None
    name: Optional[str] = None
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

    class Config:
        from_attributes = True

class Group(GroupInDBBase):
    pass

class GroupSearchResponse(BaseModel):
    items: List[Group]
    total: int
    skip: int
    limit: int 
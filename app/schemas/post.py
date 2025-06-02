from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.db.models.post import PostStatusEnum


class PostImageCreate(BaseModel):
    url: str


class PostImageOut(PostImageCreate):
    image_id: UUID

class PostBase(BaseModel):
    title: str
    content: str
    status: Optional[PostStatusEnum] = PostStatusEnum.waiting
    rejection_reason: Optional[str] = None


class PostCreate(PostBase):
    tag_ids: List[UUID] = []
    material_ids: List[UUID] = []
    topic_ids: List[UUID] = []
    images: List[PostImageCreate] = []
    created_by: Optional[UUID]


class PostUpdate(PostBase):
    tag_ids: Optional[List[UUID]] = None
    material_ids: Optional[List[UUID]] = None
    topic_ids: Optional[List[UUID]] = None
    images: Optional[List[PostImageCreate]] = None
    updated_by: Optional[UUID]


class PostOut(PostBase):
    post_id: UUID
    created_at: datetime
    updated_at: datetime
    tags: List = []
    materials: List = []
    topics: List = []
    images: List[PostImageOut] = []

    class Config:
        orm_mode = True

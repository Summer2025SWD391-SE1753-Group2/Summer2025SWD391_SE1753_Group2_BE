from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.db.models.post import PostStatusEnum
from app.schemas.tag import TagOut
from app.schemas.material import MaterialOut
from app.schemas.topic import TopicOut
from app.schemas.post_material import PostMaterialCreate, PostMaterialOut

class PostImageCreate(BaseModel):
    image_url: str

class PostImageOut(PostImageCreate):
    image_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    status: Optional[PostStatusEnum] = PostStatusEnum.waiting
    rejection_reason: Optional[str] = None

class PostCreate(PostBase):
    tag_ids: List[UUID] = []
    materials: List[PostMaterialCreate] = []  # Changed from material_ids
    topic_ids: List[UUID] = []
    images: List[str] = []  # Chỉ cần truyền list các URL
    created_by: Optional[UUID] = None

class PostUpdate(PostBase):
    tag_ids: Optional[List[UUID]] = None
    materials: Optional[List[PostMaterialCreate]] = None  # Changed from material_ids
    topic_ids: Optional[List[UUID]] = None
    images: Optional[List[str]] = None
    updated_by: Optional[UUID] = None
class PostOut(PostBase):
    post_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: Optional[UUID]
    approved_by: Optional[UUID]
    tags: List[TagOut] = []
    materials: List[PostMaterialOut] = []
    topics: List[TopicOut] = []
    images: List[PostImageOut] = []

    class Config:
        orm_mode = True

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from uuid import UUID
from typing import Dict, Any
from datetime import datetime
from app.db.models.post import PostStatusEnum
from app.schemas.tag import TagOut
from app.schemas.material import MaterialOut
from app.schemas.topic import TopicOut
from app.schemas.step import StepCreate, StepOut
from app.schemas.post_material import PostMaterialCreate, PostMaterialOut
import logging
logger = logging.getLogger(__name__)
class PostImageCreate(BaseModel):
    image_url: str

class PostImageOut(PostImageCreate):
    image_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    content: str = Field(..., min_length=1)
    status: Optional[PostStatusEnum] = PostStatusEnum.waiting
    rejection_reason: Optional[str] = None

class PostCreate(PostBase):
    tag_ids: List[UUID] = []
    materials: List[PostMaterialCreate] = Field(..., min_items=1)  # Changed from material_ids
    topic_ids: List[UUID] = Field(..., min_items=1)
    images: List[str] = []  # Chỉ cần truyền list các URL
    steps: List[StepCreate] = []
    created_by: Optional[UUID] = None

class PostUpdate(PostBase):
    tag_ids: Optional[List[UUID]] = None
    materials: Optional[List[PostMaterialCreate]] = None  # Changed from material_ids
    topic_ids: Optional[List[UUID]] = None
    images: Optional[List[str]] = None
    steps: Optional[List[StepCreate]] = None
    updated_by: Optional[UUID] = None
class PostOut(BaseModel):
    post_id: UUID
    title: str
    content: str
    status: PostStatusEnum
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: Optional[UUID]
    approved_by: Optional[UUID]
    tags: List[TagOut] = Field(default_factory=list)
    steps: List[StepOut] = Field(default_factory=list)
    materials: List[Dict[str, Any]] = Field(default_factory=list)
    topics: List[TopicOut] = Field(default_factory=list)
    images: List[PostImageOut] = Field(default_factory=list)

    @classmethod
    def from_orm(cls, db_obj):
        logger.info(f"Converting post {db_obj.post_id} to PostOut")
        steps = [StepOut.from_orm(step) for step in sorted(db_obj.steps, key=lambda x: x.order_number)]
        # Convert tags to TagOut
        tags = [TagOut.from_orm(tag) for tag in db_obj.tags]
        logger.info(f"Converted {len(tags)} tags")

        # Convert topics to TopicOut
        topics = [TopicOut.from_orm(topic) for topic in db_obj.topics]
        logger.info(f"Converted {len(topics)} topics")

        # Convert images to PostImageOut
        images = [PostImageOut.from_orm(image) for image in db_obj.images]
        logger.info(f"Converted {len(images)} images")

        # Convert materials
        materials = []
        for pm in db_obj.post_materials:
            if pm.material:
                material_dict = {
                    "material_id": str(pm.material.material_id),
                    "material_name": pm.material.name,
                    "unit": pm.material.unit,
                    "quantity": float(pm.quantity)
                }
                materials.append(material_dict)
        logger.info(f"Converted {len(materials)} materials")

        # Create dict with all fields
        obj_dict = {
            "post_id": db_obj.post_id,
            "title": db_obj.title,
            "content": db_obj.content,
            "status": db_obj.status,
            "rejection_reason": db_obj.rejection_reason,
            "created_at": db_obj.created_at,
            "updated_at": db_obj.updated_at,
            "created_by": db_obj.created_by,
            "updated_by": db_obj.updated_by,
            "approved_by": db_obj.approved_by,
            "tags": tags,
            "steps": steps,
            "topics": topics,
            "images": images,
            "materials": materials
        }

        return cls(**obj_dict)

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
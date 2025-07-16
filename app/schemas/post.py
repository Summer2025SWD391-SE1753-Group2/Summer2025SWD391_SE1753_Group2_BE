from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import List, Optional
from uuid import UUID
from typing import Dict, Any
from datetime import datetime
from enum import Enum
from app.db.models.post import PostStatusEnum
from app.schemas.tag import TagOut
from app.schemas.material import MaterialOut
from app.schemas.topic import TopicOut
from app.schemas.step import StepCreate, StepOut
from app.schemas.post_material import PostMaterialCreate, PostMaterialOut
from app.schemas.common import AccountSummary
import logging
logger = logging.getLogger(__name__)

class PostStatusEnum(str, Enum):
    waiting = "waiting"
    approved = "approved"
    rejected = "rejected"

class UserInfoOut(BaseModel):
    """Schema for user information in posts"""
    account_id: UUID
    username: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None

    model_config = {
        'from_attributes': True
    }

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
    rejection_reason: Optional[str] = None

class PostCreate(PostBase):
    tag_ids: List[UUID] = []
    materials: List[PostMaterialCreate] = Field(..., min_items=1)
    topic_ids: List[UUID] = Field(..., min_items=1)
    images: List[str] = []
    steps: List[StepCreate] = []
    created_by: Optional[UUID] = None
    status: Optional[PostStatusEnum] = None

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    content: Optional[str] = Field(None, min_length=1)
    rejection_reason: Optional[str] = None
    tag_ids: Optional[List[UUID]] = None
    materials: Optional[List[PostMaterialCreate]] = None
    topic_ids: Optional[List[UUID]] = None
    images: Optional[List[str]] = None
    steps: Optional[List[StepCreate]] = None
    updated_by: Optional[UUID] = None

class PostModeration(BaseModel):
    status: PostStatusEnum
    rejection_reason: Optional[str] = None
    approved_by: UUID

    @field_validator('rejection_reason')
    @classmethod
    def validate_rejection_reason(cls, v: Optional[str], info: ValidationInfo) -> Optional[str]:
        if info.data.get('status') == PostStatusEnum.rejected and not v:
            raise ValueError('Rejection reason is required when status is rejected')
        return v

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
    creator: Optional[UserInfoOut] = None
    updater: Optional[UserInfoOut] = None
    approver: Optional[UserInfoOut] = None
    tags: List[TagOut] = Field(default_factory=list)
    steps: List[StepOut] = Field(default_factory=list)
    materials: List[PostMaterialOut] = Field(default_factory=list)
    topics: List[TopicOut] = Field(default_factory=list)
    images: List[PostImageOut] = Field(default_factory=list)

    # Use model_config instead of Config class for Pydantic v2
    model_config = {
        'from_attributes': True,
        'json_encoders': {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    }

    # Replace from_orm with a custom method that works with model_validate
    @classmethod
    def from_db_model(cls, db_obj):
        logger.info(f"Converting post {db_obj.post_id} to PostOut")
        
        # Convert creator info
        creator = None
        if hasattr(db_obj, 'creator') and db_obj.creator:
            creator = AccountSummary.model_validate(db_obj.creator)
        
        # Convert steps
        steps = [StepOut.model_validate(step) for step in sorted(db_obj.steps, key=lambda x: x.order_number)]
        
        # Convert tags to TagOut
        tags = [TagOut.model_validate(tag) for tag in db_obj.tags]
        logger.info(f"Converted {len(tags)} tags")

        # Convert topics to TopicOut
        topics = [TopicOut.model_validate(topic) for topic in db_obj.topics]
        logger.info(f"Converted {len(topics)} topics")

        # Convert images to PostImageOut
        images = [PostImageOut.model_validate(image) for image in db_obj.images]
        logger.info(f"Converted {len(images)} images")

        # Convert materials
        materials = []
        for pm in getattr(db_obj, 'post_materials', []):
            if hasattr(pm, 'material') and pm.material is not None:
                material_out = PostMaterialOut.from_sqlalchemy(pm)
                materials.append(material_out)
        
        logger.info(f"Final materials in PostOut: {materials}")
        logger.info(f"Materials count: {len(materials)}")

        # Convert user relationships
        creator = UserInfoOut.model_validate(db_obj.creator) if db_obj.creator else None
        updater = UserInfoOut.model_validate(db_obj.updater) if db_obj.updater else None
        approver = UserInfoOut.model_validate(db_obj.approver) if db_obj.approver else None

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
            "creator": creator,
            "updater": updater,
            "approver": approver,
            "tags": tags,
            "steps": steps,
            "topics": topics,
            "images": images,
            "materials": materials
        }

        return cls.model_validate(obj_dict)
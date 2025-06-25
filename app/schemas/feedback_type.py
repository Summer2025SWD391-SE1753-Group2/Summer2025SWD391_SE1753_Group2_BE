from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum
from app.schemas.common import AccountSummary

class FeedbackTypeStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class FeedbackTypeBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Unique name for the feedback type")
    display_name: str = Field(..., min_length=2, max_length=200, description="Display name shown to users")
    description: Optional[str] = Field(None, description="Description of the feedback type")
    icon: Optional[str] = Field(None, max_length=100, description="Icon class or URL")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code")
    sort_order: str = Field(default="0", description="Sort order for UI display")

class FeedbackTypeCreate(FeedbackTypeBase):
    created_by: Optional[UUID] = None

class FeedbackTypeUpdate(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    status: Optional[FeedbackTypeStatusEnum] = None
    sort_order: Optional[str] = None
    updated_by: Optional[UUID] = None

class FeedbackTypeOut(FeedbackTypeBase):
    feedback_type_id: UUID
    is_default: bool
    status: FeedbackTypeStatusEnum
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    
    # Related account information
    creator: Optional[AccountSummary] = None
    updater: Optional[AccountSummary] = None

    model_config = ConfigDict(from_attributes=True, json_encoders={
        datetime: lambda v: v.isoformat(),
        UUID: lambda v: str(v)
    })

class FeedbackTypeList(BaseModel):
    feedback_types: List[FeedbackTypeOut]
    total: int
    skip: int
    limit: int 
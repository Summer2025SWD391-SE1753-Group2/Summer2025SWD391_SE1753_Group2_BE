from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class FeedbackStatusEnum(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"

class FeedbackPriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"

class FeedbackBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=300, description="Feedback title")
    description: str = Field(..., min_length=10, description="Detailed description of the feedback")
    feedback_type_id: UUID = Field(..., description="ID of the feedback type")
    priority: FeedbackPriorityEnum = Field(default=FeedbackPriorityEnum.medium, description="Priority level")
    screenshot_url: Optional[str] = Field(None, description="URL to screenshot if applicable")
    browser_info: Optional[str] = Field(None, max_length=200, description="Browser information")
    device_info: Optional[str] = Field(None, max_length=200, description="Device information")

class FeedbackCreate(FeedbackBase):
    pass

class FeedbackUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=300)
    description: Optional[str] = Field(None, min_length=10)
    feedback_type_id: Optional[UUID] = None
    priority: Optional[FeedbackPriorityEnum] = None
    status: Optional[FeedbackStatusEnum] = None
    resolution_note: Optional[str] = Field(None, description="Note from moderator/admin when resolving")
    screenshot_url: Optional[str] = None
    browser_info: Optional[str] = Field(None, max_length=200)
    device_info: Optional[str] = Field(None, max_length=200)

class FeedbackResolution(BaseModel):
    status: FeedbackStatusEnum = Field(..., description="New status (resolved/rejected)")
    resolution_note: str = Field(..., min_length=5, description="Explanation of resolution")

class AccountSummary(BaseModel):
    account_id: UUID
    username: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class FeedbackTypeSummary(BaseModel):
    feedback_type_id: UUID
    name: str
    display_name: str
    icon: Optional[str] = None
    color: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class FeedbackOut(FeedbackBase):
    feedback_id: UUID
    status: FeedbackStatusEnum
    resolution_note: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: Optional[UUID] = None
    resolved_by: Optional[UUID] = None
    
    # Related information
    creator: AccountSummary
    updater: Optional[AccountSummary] = None
    resolver: Optional[AccountSummary] = None
    feedback_type: FeedbackTypeSummary

    model_config = ConfigDict(from_attributes=True, json_encoders={
        datetime: lambda v: v.isoformat(),
        UUID: lambda v: str(v)
    })

class FeedbackList(BaseModel):
    feedbacks: List[FeedbackOut]
    total: int
    skip: int
    limit: int 
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class ReportTypeEnum(str, Enum):
    report_material = "report_material"
    report_tag = "report_tag"
    report_topic = "report_topic"
    report_post = "report_post"
    report_other = "report_other"

class ReportStatusEnum(str, Enum):
    pending = "pending"
    approve = "approve"
    reject = "reject"

class ReportCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    type: ReportTypeEnum
    reason: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    unit: str | None = None
    object_add: str | None = None

class ReportUpdate(BaseModel):
    status: ReportStatusEnum
    reject_reason: str | None = None
    unit: str | None = None
    object_add: str | None = None

class ReportOut(BaseModel):
    report_id: UUID
    title: str
    type: ReportTypeEnum
    reason: str
    status: ReportStatusEnum
    description: str | None = None
    reject_reason: str | None = None
    unit: str | None = None
    object_add: str | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

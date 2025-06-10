from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MaterialStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"


# Base schema chứa các trường chung
class MaterialBase(BaseModel):
    name: str = Field(..., max_length=150)
    status: MaterialStatusEnum = MaterialStatusEnum.active
    image_url: Optional[str] = Field(None, max_length=500)
    unit: str  # Add unit field



# Schema cho việc tạo mới
class MaterialCreate(MaterialBase):
    created_by: Optional[UUID] = None


# Schema cho việc cập nhật
class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    status: Optional[MaterialStatusEnum] = None
    image_url: Optional[str] = Field(None, max_length=500)
    unit: Optional[str] = None 


# Schema khi trả về dữ liệu
class MaterialOut(MaterialBase):
    material_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    class Config:
        orm_mode = True

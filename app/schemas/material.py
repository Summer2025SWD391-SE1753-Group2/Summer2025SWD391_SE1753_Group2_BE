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
    unit_id: UUID  # Tham chiếu tới unit



# Schema cho việc tạo mới
class MaterialCreate(MaterialBase):
    created_by: Optional[UUID] = None


# Schema cho việc cập nhật
class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=150)
    status: Optional[MaterialStatusEnum] = None
    image_url: Optional[str] = Field(None, max_length=500)
    unit_id: Optional[UUID] = None


# Schema khi trả về dữ liệu
class MaterialOut(MaterialBase):
    material_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]
    unit_name: str  # Lấy từ unit.name

    @classmethod
    def from_orm(cls, obj):
        return cls(
            material_id=obj.material_id,
            name=obj.name,
            status=obj.status,
            image_url=obj.image_url,
            unit_id=obj.unit_id,
            unit_name=obj.unit.name if obj.unit else None,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            created_by=obj.created_by,
            updated_by=obj.updated_by,
        )

    class Config:
        orm_mode = True

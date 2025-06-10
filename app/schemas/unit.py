from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class UnitStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class UnitBase(BaseModel):
    name: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    status: Optional[UnitStatusEnum] = UnitStatusEnum.active

class UnitCreate(UnitBase):
    created_by: Optional[UUID] = None

class UnitUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=200)
    status: Optional[UnitStatusEnum] = None

class UnitOut(UnitBase):
    unit_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)
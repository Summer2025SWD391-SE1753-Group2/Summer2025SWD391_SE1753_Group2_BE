from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID

class StepCreate(BaseModel):
    order_number: int = Field(..., ge=1, le=20, description="Step number (1-20)")
    content: str = Field(..., min_length=1, description="Step content")

    @field_validator('order_number')
    def validate_order_number(cls, v):
        if not 1 <= v <= 20:
            raise ValueError('Step number must be between 1 and 20')
        return v
class StepOut(BaseModel):
    step_id: UUID
    order_number: int
    content: str

    class Config:
        from_attributes = True
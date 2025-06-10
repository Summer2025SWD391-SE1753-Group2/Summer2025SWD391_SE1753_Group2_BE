from pydantic import BaseModel, Field
from uuid import UUID

class PostMaterialCreate(BaseModel):
    material_id: UUID
    quantity: float = Field(..., gt=0)

class PostMaterialOut(BaseModel):
    material_id: UUID
    material_name: str
    unit: str  # This will come from the material
    quantity: float
    
    class Config:
        from_attributes = True
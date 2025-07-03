from pydantic import BaseModel, Field
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
class PostMaterialCreate(BaseModel):
    material_id: UUID
    quantity: float = Field(..., gt=0)

class PostMaterialOut(BaseModel):
    material_id: UUID
    material_name: str
    unit: str
    quantity: float

    model_config = {'from_attributes': True}

    @classmethod
    def from_sqlalchemy(cls, obj):
        # Chuẩn hóa cho Pydantic V2: dùng model_validate
        return cls.model_validate({
            "material_id": obj.material.material_id,
            "material_name": obj.material.name,
            "unit": obj.unit,
            "quantity": obj.quantity
        })
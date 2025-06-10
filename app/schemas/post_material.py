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

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }

    @classmethod
    def from_orm(cls, obj):
        logger.info(f"Converting ORM object to PostMaterialOut: {obj.__dict__}")
        try:
            return cls(
                material_id=obj.material.material_id,
                material_name=obj.material.name,
                unit=obj.material.unit,
                quantity=obj.quantity
            )
        except Exception as e:
            logger.error(f"Error converting ORM object: {str(e)}", exc_info=True)
            raise
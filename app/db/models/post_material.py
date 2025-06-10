from sqlalchemy import Column, ForeignKey, Float, String
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class PostMaterial(Base):
    __tablename__ = "post_material"

    post_id = Column(UUID(as_uuid=True), ForeignKey("post.post_id"), primary_key=True)
    material_id = Column(UUID(as_uuid=True), ForeignKey("material.material_id"), primary_key=True)
    quantity = Column(Float, nullable=False)

    # Add relationships
    post = relationship("Post", back_populates="post_materials")
    material = relationship("Material", back_populates="post_materials")
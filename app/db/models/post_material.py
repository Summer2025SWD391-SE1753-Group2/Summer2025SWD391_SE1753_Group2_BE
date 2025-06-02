from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
from sqlalchemy.orm import relationship

post_material = Table(
    "post_material",
    Base.metadata,
    Column("post_id", UUID(as_uuid=True), ForeignKey("post.post_id"), primary_key=True),
    Column("material_id", UUID(as_uuid=True), ForeignKey("material.material_id"), primary_key=True),
)

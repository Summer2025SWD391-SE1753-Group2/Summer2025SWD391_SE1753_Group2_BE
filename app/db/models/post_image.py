from sqlalchemy import Column, String, ForeignKey, UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import uuid

class PostImage(Base):
    __tablename__ = "post_image"

    post_image_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.post_id"), nullable=False)
    image_url = Column(String(255), nullable=False)

    # Relationships
    post = relationship("Post", back_populates="images") 
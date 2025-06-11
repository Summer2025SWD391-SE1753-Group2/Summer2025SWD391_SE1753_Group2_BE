from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base_class import Base

class Step(Base):
    __tablename__ = "step"

    step_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("post.post_id", ondelete="CASCADE"))
    order_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    post = relationship("Post", back_populates="steps")
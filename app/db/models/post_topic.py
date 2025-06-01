from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
from sqlalchemy.orm import relationship

post_topic = Table(
    "post_topic",
    Base.metadata,
    Column("post_id", UUID(as_uuid=True), ForeignKey("post.post_id"), primary_key=True),
    Column("topic_id", UUID(as_uuid=True), ForeignKey("topic.topic_id"), primary_key=True),
)
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid

class ReportTypeEnum(str, enum.Enum):
    report_material = "report_material"
    report_tag = "report_tag"
    report_topic = "report_topic"
    report_post = "report_post"
    report_other = "report_other"

class ReportStatusEnum(str, enum.Enum):
    pending = "pending"
    approve = "approve"
    reject = "reject"

class Report(Base):
    __tablename__ = "report"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String(255), nullable=False)
    type = Column(Enum(ReportTypeEnum), nullable=False)
    reason = Column(String(255), nullable=False)
    status = Column(Enum(ReportStatusEnum), default=ReportStatusEnum.pending)
    description = Column(Text, nullable=True)
    reject_reason = Column(Text, nullable=True)
    object_add = Column(Text, nullable=True)
    unit = Column(String(255), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("account.account_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


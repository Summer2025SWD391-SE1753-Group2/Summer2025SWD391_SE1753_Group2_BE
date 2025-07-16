from sqlalchemy.orm import Session
from app.db.models.report import Report, ReportStatusEnum, ReportTypeEnum
from app.schemas.report import ReportCreate, ReportUpdate
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, timezone
from typing import List

def create_report(db: Session, report_data: ReportCreate, created_by: UUID) -> Report:
    report = Report(
        title=report_data.title,
        type=report_data.type,
        reason=report_data.reason,
        description=report_data.description,
        status=ReportStatusEnum.pending,
        created_by=created_by,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

def get_all_reports(db: Session, skip: int = 0, limit: int = 100) -> List[Report]:
    return db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()

def get_report_by_id(db: Session, report_id: UUID) -> Report:
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

def update_report_status(db: Session, report_id: UUID, update_data: ReportUpdate, updated_by: UUID) -> Report:
    report = get_report_by_id(db, report_id)
    if report.status != ReportStatusEnum.pending:
        raise HTTPException(status_code=400, detail="Report already processed")
    report.status = update_data.status
    report.reject_reason = update_data.reject_reason
    report.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(report)
    return report

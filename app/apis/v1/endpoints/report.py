
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.schemas.report import ReportCreate, ReportUpdate, ReportOut
from app.services.report_service import create_report, get_all_reports, get_report_by_id, update_report_status
from app.core.deps import get_db
from app.db.models.account import Account
from app.db.models.report import Report
from app.apis.v1.endpoints.check_role import check_roles
from app.schemas.account import RoleNameEnum

router = APIRouter()

@router.get("/by-user/{user_id}", response_model=List[ReportOut])
def get_reports_by_user_id(
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.admin, RoleNameEnum.moderator]))
):
    """
    Lấy danh sách report theo user_id (có phân trang).
    """
    return db.query(Report).filter(Report.created_by == user_id).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/", response_model=ReportOut, status_code=status.HTTP_201_CREATED)
def create_report_endpoint(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Tạo mới report. Truyền đủ các trường, bao gồm unit, object_add nếu có.
    """
    return create_report(db=db, report_data=report_data, created_by=current_user.account_id)


@router.get("/", response_model=List[ReportOut])
def get_reports_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.admin, RoleNameEnum.moderator]))
):
    """
    Lấy danh sách report, có phân trang.
    """
    return get_all_reports(db=db, skip=skip, limit=limit)


@router.get("/{report_id}", response_model=ReportOut)
def get_report_by_id_endpoint(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.admin, RoleNameEnum.moderator]))
):
    """
    Lấy chi tiết report theo id.
    """
    return get_report_by_id(db=db, report_id=report_id)


@router.put("/{report_id}", response_model=ReportOut)
def update_report_status_endpoint(
    report_id: UUID,
    update_data: ReportUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin, RoleNameEnum.moderator]))
):
    """
    Cập nhật trạng thái, reject_reason, unit, object_add cho report.
    """
    return update_report_status(db=db, report_id=report_id, update_data=update_data, updated_by=current_user.account_id)

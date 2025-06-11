from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.group import Group, GroupCreate, GroupUpdate, GroupSearchResponse
from app.services import group as group_service
from uuid import UUID
from app.db.models.account import Account
from app.schemas.account import RoleNameEnum
from app.apis.v1.endpoints.check_role import check_roles

router = APIRouter()

@router.post("/", response_model=Group)
def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    return group_service.create_group(
        db=db,
        group=group,
        created_by=current_account.account_id,
        role=current_account.role.role_name
    )

@router.get("/{group_id}", response_model=Group)
def get_group(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    db_group = group_service.get_group(db=db, group_id=group_id)
    if not db_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    return db_group

@router.get("/", response_model=List[Group])
def get_groups(
    skip: int = 0,
    limit: int = 100,
    topic_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    return group_service.get_groups(
        db=db,
        skip=skip,
        limit=limit,
        topic_id=topic_id
    )

@router.get("/search/", response_model=GroupSearchResponse)
def search_groups(
    topic_id: Optional[UUID] = None,
    group_leader_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Search groups with pagination
    - Filter by topic_id (optional)
    - Filter by group_leader_id (optional)
    - Pagination with skip and limit
    """
    return group_service.search_groups(
        db=db,
        topic_id=topic_id,
        group_leader_id=group_leader_id,
        skip=skip,
        limit=limit
    )

@router.put("/{group_id}", response_model=Group)
def update_group(
    group_id: UUID,
    group_update: GroupUpdate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    return group_service.update_group(
        db=db,
        group_id=group_id,
        group_update=group_update,
        role=current_account.role.role_name
    )

@router.delete("/{group_id}")
def delete_group(
    group_id: UUID,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    return group_service.delete_group(
        db=db,
        group_id=group_id,
        role=current_account.role.role_name
    ) 
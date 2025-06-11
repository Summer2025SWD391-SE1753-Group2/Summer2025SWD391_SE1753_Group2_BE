from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.schemas.group_member import GroupMember, GroupMemberCreate, GroupMemberUpdate, GroupMemberWithDetails
from app.services import group_member as group_member_service
from uuid import UUID
from app.db.models.account import Account
from app.schemas.account import RoleNameEnum
from app.apis.v1.endpoints.check_role import check_roles

router = APIRouter()

@router.post("/", response_model=GroupMember)
def create_group_member(
    member: GroupMemberCreate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Add a member to a group
    Only moderator and admin can add members
    """
    try:
        return group_member_service.create_group_member(db=db, member=member)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{group_member_id}", response_model=GroupMember)
def get_group_member(
    group_member_id: UUID,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Get a specific group member
    All authenticated users can view group members
    """
    db_member = group_member_service.get_group_member(db=db, group_member_id=group_member_id)
    if not db_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group member not found"
        )
    return db_member

@router.get("/", response_model=List[GroupMember])
def get_group_members(
    group_id: Optional[UUID] = None,
    account_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Get list of group members
    All authenticated users can view group members
    """
    return group_member_service.get_group_members(
        db=db,
        group_id=group_id,
        account_id=account_id,
        skip=skip,
        limit=limit
    )

@router.get("/search/", response_model=GroupMemberWithDetails)
def search_group_members(
    group_id: UUID = Query(..., description="Group ID to search members for"),
    account_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Search group members with pagination
    All authenticated users can search group members
    Required:
    - group_id: UUID of the group to search members for
    Optional:
    - account_id: UUID of the account to filter by
    - skip: Number of items to skip (default: 0)
    - limit: Number of items per page (default: 10, max: 100)
    """
    try:
        return group_member_service.search_group_members(
            db=db,
            group_id=group_id,
            account_id=account_id,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{group_member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group_member(
    group_member_id: UUID,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Remove a member from a group
    Only moderator and admin can remove members
    """
    try:
        group_member_service.delete_group_member(db=db, group_member_id=group_member_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.deps import get_db
from app.apis.v1.endpoints.check_role import check_roles
from app.schemas.unit import UnitCreate, UnitUpdate, UnitOut
from app.services import unit_service
from app.db.models.account import Account
from app.schemas.account import RoleNameEnum

router = APIRouter()

@router.post("/", response_model=UnitOut, status_code=status.HTTP_201_CREATED)
def create_unit(
    unit: UnitCreate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin, RoleNameEnum.moderator]))
) -> UnitOut:
    unit.created_by = current_user.account_id
    return unit_service.create_unit(db, unit, current_user.account_id)

@router.get("/", response_model=List[UnitOut])
def read_units(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[UnitOut]:
    return unit_service.get_all_units(db, skip=skip, limit=limit)

@router.get("/{unit_id}", response_model=UnitOut)
def read_unit(
    unit_id: UUID,
    db: Session = Depends(get_db)
) -> UnitOut:
    return unit_service.get_unit_by_id(db, unit_id)

@router.put("/{unit_id}", response_model=UnitOut)
def update_unit(
    unit_id: UUID,
    unit: UnitUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin, RoleNameEnum.moderator]))
) -> UnitOut:
    return unit_service.update_unit(db, unit_id, unit, current_user.account_id)

@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_unit(
    unit_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    unit_service.delete_unit(db, unit_id)
    return
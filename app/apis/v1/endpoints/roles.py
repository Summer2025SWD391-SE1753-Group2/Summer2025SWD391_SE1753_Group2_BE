from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.role import RoleCreate, RoleOut
from app.services.role_service import create_role
from app.core.deps import get_db

router = APIRouter()

@router.post("/", response_model=RoleOut)
def create_new_role(role: RoleCreate, db: Session = Depends(get_db)):
    return create_role(db, role)

@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: int, db: Session = Depends(get_db)):
    from app.services.role_service import get_role_by_id
    return get_role_by_id(db, role_id)

@router.get("/", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    from app.services.role_service import get_all_roles
    return get_all_roles(db)
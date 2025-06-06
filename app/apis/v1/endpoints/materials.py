from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.models.account import Account
from app.apis.v1.endpoints.check_role import get_current_user

from app.core.deps import get_db
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialOut
from app.services.material_service import (
    create_material,
    get_material_by_id,
    get_all_materials,
    update_material,
    delete_material,
)

router = APIRouter()


@router.post("/", response_model=MaterialOut, status_code=status.HTTP_201_CREATED)
def create_material_endpoint(
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
):
    # Bạn có thể truyền user_id thực tế ở đây nếu có hệ thống auth
    dummy_user_id = material_data.created_by or UUID("00000000-0000-0000-0000-000000000000")
    return create_material(db, material_data, created_by=dummy_user_id)


@router.get("/{material_id}", response_model=MaterialOut)
def get_material_by_id_endpoint(material_id: UUID, db: Session = Depends(get_db)):
    material = get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.get("/", response_model=List[MaterialOut])
def get_all_materials_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_materials(db, skip=skip, limit=limit)


@router.put("/{material_id}", response_model=MaterialOut)
def update_material_endpoint(
    material_id: UUID,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    material = get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return update_material(db, material_id, material_data, updated_by=current_user.account_id)

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material_endpoint(
    material_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_user)
):
    material = get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    delete_material(db, material_id)
    return

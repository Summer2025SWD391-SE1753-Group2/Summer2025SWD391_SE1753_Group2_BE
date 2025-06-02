from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.core.deps import get_db
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialOut
from app.services.material_service import (
    create_material,
    get_material_by_id,
    get_all_materials,
    update_material,
    delete_material,
)

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.post("/", response_model=MaterialOut, status_code=status.HTTP_201_CREATED)
async def create_material_endpoint(
    material_data: MaterialCreate,
    db: Session = Depends(get_db),
):
    # Bạn có thể truyền user_id thực tế ở đây nếu có hệ thống auth
    dummy_user_id = material_data.created_by or UUID("00000000-0000-0000-0000-000000000000")
    return await create_material(db, material_data, created_by=dummy_user_id)


@router.get("/{material_id}", response_model=MaterialOut)
async def get_material_by_id_endpoint(material_id: UUID, db: Session = Depends(get_db)):
    material = get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.get("/", response_model=List[MaterialOut])
async def get_all_materials_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_materials(db, skip=skip, limit=limit)


@router.put("/{material_id}", response_model=MaterialOut)
async def update_material_endpoint(
    material_id: UUID,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
):
    existing_material = get_material_by_id(db, material_id)
    if not existing_material:
        raise HTTPException(status_code=404, detail="Material not found")

    dummy_user_id = material_data.updated_by or UUID("00000000-0000-0000-0000-000000000000")
    return await update_material(db, material_id, material_data, updated_by=dummy_user_id)


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material_endpoint(material_id: UUID, db: Session = Depends(get_db)):
    material = get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    delete_material(db, material_id)
    return

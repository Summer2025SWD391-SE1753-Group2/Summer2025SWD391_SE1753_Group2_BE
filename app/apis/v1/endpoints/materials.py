from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.db.models.account import Account
from app.apis.v1.endpoints.check_role import get_current_user
from app.schemas.account import RoleNameEnum
from app.apis.v1.endpoints.check_role import check_roles
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
    current_user: Account = Depends(check_roles([RoleNameEnum.admin, RoleNameEnum.moderator]))
):
    return create_material(
        db=db, 
        material_data=material_data, 
        created_by=current_user.account_id
    )


@router.get("/{material_id}", response_model=MaterialOut)
def get_material_by_id_endpoint(material_id: UUID, db: Session = Depends(get_db)):
    material = get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


@router.get("/", response_model=List[MaterialOut])
def get_all_materials_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    materials = get_all_materials(db, skip=skip, limit=limit)
    return [MaterialOut.from_orm(m) for m in materials]


@router.put("/{material_id}", response_model=MaterialOut)
def update_material_endpoint(
    material_id: UUID,
    material_data: MaterialUpdate,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin, RoleNameEnum.moderator]))
):
    """Update a material"""
    material = get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    try:
        return update_material(
            db=db,
            material_id=material_id, 
            material_data=material_data, 
            updated_by=current_user.account_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material_endpoint(
    material_id: UUID,
    db: Session = Depends(get_db),
    current_user: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    material = get_material_by_id(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Check if material is being used in any posts
    if material.post_materials:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete material that is being used in posts"
        )
        
    delete_material(db, material_id)
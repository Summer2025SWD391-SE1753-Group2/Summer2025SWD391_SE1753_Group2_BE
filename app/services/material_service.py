from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import text
from uuid import UUID
from app.db.models.unit import Unit
from datetime import datetime, timezone

from app.db.models.material import Material, MaterialStatusEnum
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialListResponse, MaterialOut


def check_material_name_unique(db: Session, name: str):
    existing_material = db.execute(
        text("SELECT 1 FROM material WHERE name = :name"),
        {"name": name}
    ).first()
    if existing_material:
        raise HTTPException(status_code=400, detail="Material name already exists")


def create_material(db: Session, material_data: MaterialCreate, created_by: UUID) -> MaterialOut:
    try:
        # Verify unit exists
        unit = db.query(Unit).filter(Unit.unit_id == material_data.unit_id).first()
        if not unit:
            raise HTTPException(status_code=400, detail=f"Unit with ID {material_data.unit_id} not found")

        material = Material(
            name=material_data.name,
            status=material_data.status,
            image_url=material_data.image_url,
            unit_id=material_data.unit_id,
            created_by=created_by,
            updated_by=created_by
        )
        
        db.add(material)
        db.commit()
        db.refresh(material)
        
        # Load unit relationship and return MaterialOut
        material_with_unit = db.query(Material).options(
            joinedload(Material.unit)
        ).filter(Material.material_id == material.material_id).first()
        
        return MaterialOut.from_orm(material_with_unit)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def get_material_by_id(db: Session, material_id: UUID) -> MaterialOut:
    material = db.query(Material).options(
        joinedload(Material.unit)
    ).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return MaterialOut.from_orm(material)


def get_all_materials(db: Session, skip: int = 0, limit: int = 100) -> MaterialListResponse:
    # Get total count
    total = db.query(Material).count()
    
    # Get paginated results with unit relationship
    materials = db.query(Material).options(
        joinedload(Material.unit)
    ).offset(skip).limit(limit).all()
    
    return MaterialListResponse(
        materials=[MaterialOut.from_orm(m) for m in materials],
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total
    )


def update_material(db: Session, material_id: UUID, material_data: MaterialUpdate, updated_by: UUID) -> MaterialOut:
    # Get material with unit relationship
    material = db.query(Material).options(
        joinedload(Material.unit)
    ).filter(Material.material_id == material_id).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    try:
        # Handle name update
        if material_data.name is not None:
            # Check if new name is unique (if it's different from current name)
            if material_data.name != material.name:
                check_material_name_unique(db, material_data.name)
            material.name = material_data.name

        # Handle status update    
        if material_data.status is not None:
            material.status = material_data.status

        # Handle image update    
        if material_data.image_url is not None:
            material.image_url = material_data.image_url

        # Handle unit update    
        if material_data.unit_id is not None:
            # Verify new unit exists
            unit = db.query(Unit).filter(Unit.unit_id == material_data.unit_id).first()
            if not unit:
                raise HTTPException(status_code=400, detail=f"Unit with ID {material_data.unit_id} not found")
            material.unit_id = material_data.unit_id
        
        material.updated_by = updated_by
        
        db.commit()
        db.refresh(material)
        
        # Return MaterialOut with unit information
        return MaterialOut.from_orm(material)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Material name already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

def delete_material(db: Session, material_id: UUID):
    material = get_material_by_id(db, material_id)
    db.delete(material)
    db.commit()
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import text
from uuid import UUID

from app.db.models.material import Material, MaterialStatusEnum
from app.schemas.material import MaterialCreate, MaterialUpdate


def check_material_name_unique(db: Session, name: str):
    existing_material = db.execute(
        text("SELECT 1 FROM material WHERE name = :name"),
        {"name": name}
    ).first()
    if existing_material:
        raise HTTPException(status_code=400, detail="Material name already exists")


async def create_material(db: Session, material_data: MaterialCreate, created_by: UUID) -> Material:
    try:
        print(f"[LOG] Create material with data: {material_data}, created_by: {created_by}")
        check_material_name_unique(db, name=material_data.name)

        db_material = Material(
            name=material_data.name,
            status=material_data.status or MaterialStatusEnum.active,
            image_url=material_data.image_url,
            created_by=created_by,
            updated_by=created_by,
        )

        db.add(db_material)
        db.commit()
        db.refresh(db_material)
        print(f"[LOG] Create material successfully: {db_material}")
        return db_material

    except IntegrityError as e:
        db.rollback()
        print(f"[ERROR] IntegrityError when creating material: {e}")
        if "material_name_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Material name already exists")
        raise HTTPException(status_code=400, detail="Failed to create material")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Exception when creating material: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def get_material_by_id(db: Session, material_id: UUID) -> Material:
    material = db.query(Material).filter(Material.material_id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material


def get_all_materials(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Material).offset(skip).limit(limit).all()


async def update_material(db: Session, material_id: UUID, material_update: MaterialUpdate, updated_by: UUID) -> Material:
    material = get_material_by_id(db, material_id)

    if material_update.name and material_update.name != material.name:
        check_material_name_unique(db, name=material_update.name)
        material.name = material_update.name

    if material_update.status:
        material.status = material_update.status

    if material_update.image_url is not None:
        material.image_url = material_update.image_url

    material.updated_by = updated_by

    db.commit()
    db.refresh(material)
    return material


def delete_material(db: Session, material_id: UUID):
    material = get_material_by_id(db, material_id)
    db.delete(material)
    db.commit()

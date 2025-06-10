from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from sqlalchemy import text
from uuid import UUID
from datetime import datetime, timezone
from app.db.models.unit import Unit, UnitStatusEnum
from app.schemas.unit import UnitCreate, UnitUpdate
from typing import List
def check_unit_name_unique(db: Session, name: str):
    existing_unit = db.execute(
        text("SELECT 1 FROM unit WHERE name = :name"),
        {"name": name}
    ).first()
    if existing_unit:
        raise HTTPException(status_code=400, detail="Unit name already exists")
def search_units_by_name(db: Session, name: str, skip: int = 0, limit: int = 100) -> List[Unit]:
    """
    Search units by name using partial match (case-insensitive)
    """
    return db.query(Unit)\
        .filter(Unit.name.ilike(f"%{name}%"))\
        .offset(skip)\
        .limit(limit)\
        .all()
def create_unit(db: Session, unit_data: UnitCreate, created_by: UUID) -> Unit:
    try:
        check_unit_name_unique(db, name=unit_data.name)

        db_unit = Unit(
            name=unit_data.name,
            description=unit_data.description,
            status=unit_data.status or UnitStatusEnum.active,
            created_by=created_by,
            updated_by=created_by
        )

        db.add(db_unit)
        db.commit()
        db.refresh(db_unit)
        return db_unit
    except IntegrityError as e:
        db.rollback()
        if "unit_name_key" in str(e.orig):
            raise HTTPException(status_code=400, detail="Unit name already exists")
        raise HTTPException(status_code=400, detail="Failed to create unit")

def get_unit_by_id(db: Session, unit_id: UUID) -> Unit:
    unit = db.query(Unit).filter(Unit.unit_id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit

def get_all_units(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Unit).offset(skip).limit(limit).all()

def update_unit(db: Session, unit_id: UUID, unit_update: UnitUpdate, updated_by: UUID) -> Unit:
    unit = get_unit_by_id(db, unit_id)

    if unit_update.description is not None:
        unit.description = unit_update.description

    if unit_update.status is not None:
        unit.status = unit_update.status

    unit.updated_by = updated_by
    unit.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(unit)
    return unit

def delete_unit(db: Session, unit_id: UUID):
    unit = get_unit_by_id(db, unit_id)
    db.delete(unit)
    db.commit()
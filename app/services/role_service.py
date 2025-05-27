from sqlalchemy.orm import Session
from app.db.models.role import Role
from app.schemas.role import RoleCreate

def create_role(db: Session, role: RoleCreate):
    db_role = Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_role_by_id(db: Session, role_id: int):
    return db.query(Role).filter(Role.role_id == role_id).first()

def get_all_roles(db: Session):
    return db.query(Role).all()

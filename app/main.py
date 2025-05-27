from fastapi import FastAPI
from sqlalchemy.orm import Session
from app.core.settings import settings
from app.db.database import engine, SessionLocal
from app.db.base_class import Base

# Import models để load vào metadata
from app.db.models import account, role  # sửa models -> model

# Tạo bảng
Base.metadata.create_all(bind=engine)

# Hàm seed role nếu chưa có
def seed_roles_if_not_exist(db: Session):
    from app.db.models.role import Role, RoleNameEnum, RoleStatusEnum

    if db.query(Role).count() == 0:
        roles = [
            Role(role_id=1, role_name=RoleNameEnum.user_l1, status=RoleStatusEnum.active, created_by="system", updated_by="system"),
            Role(role_id=2, role_name=RoleNameEnum.user_l2, status=RoleStatusEnum.active, created_by="system", updated_by="system"),
            Role(role_id=3, role_name=RoleNameEnum.moderator, status=RoleStatusEnum.active, created_by="system", updated_by="system"),
            Role(role_id=4, role_name=RoleNameEnum.admin, status=RoleStatusEnum.active, created_by="system", updated_by="system"),
        ]
        db.add_all(roles)
        db.commit()

# Gọi seed sau khi create_all
with SessionLocal() as db:
    seed_roles_if_not_exist(db)

# Khởi tạo FastAPI
from app.apis.v1 import base as api_v1

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(api_v1.api_router, prefix=settings.API_V1_STR)

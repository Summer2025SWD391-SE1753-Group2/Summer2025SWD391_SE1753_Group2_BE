from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.settings import settings
from app.db.database import engine, SessionLocal
from app.db.base_class import Base
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.PROJECT_NAME)

# Thêm middleware CORS ngay sau khi khởi tạo app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # FE đang chạy ở cổng 5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import models để load vào metadata
from app.db.models import account, role, message

# Tạo bảng
Base.metadata.create_all(bind=engine)

# Hàm seed role nếu chưa có
def seed_roles_if_not_exist(db: Session):
    from app.db.models.role import Role, RoleNameEnum, RoleStatusEnum

    if db.query(Role).count() == 0:
        roles = [
            Role(role_id=1, role_name=RoleNameEnum.user, status=RoleStatusEnum.active, created_by=None, updated_by=None),
            Role(role_id=2, role_name=RoleNameEnum.moderator, status=RoleStatusEnum.active, created_by=None, updated_by=None),
            Role(role_id=3, role_name=RoleNameEnum.admin, status=RoleStatusEnum.active, created_by=None, updated_by=None),
        ]
        db.add_all(roles)
        db.commit()

# Gọi seed sau khi create_all
with SessionLocal() as db:
    seed_roles_if_not_exist(db)

# Khởi tạo router
from app.apis.v1 import base as api_v1
app.include_router(api_v1.api_router, prefix=settings.API_V1_STR)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        routes=app.routes,
    )
    # Find the OAuth2PasswordBearer security scheme and update tokenUrl
    security_schemes = openapi_schema.get("components", {}).get("securitySchemes", {})
    if "OAuth2PasswordBearer" in security_schemes:
        password_flow = security_schemes["OAuth2PasswordBearer"].get("flows", {}).get("password")
        if password_flow:
            password_flow["tokenUrl"] = f"{settings.API_V1_STR}/auth/access-token"

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

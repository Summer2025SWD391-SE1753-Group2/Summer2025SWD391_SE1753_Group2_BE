from pydantic import BaseModel
from enum import Enum

class RoleNameEnum(str, Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"

class RoleStatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class RoleBase(BaseModel):
    role_name: RoleNameEnum
    status: RoleStatusEnum

class RoleCreate(RoleBase):
    created_by: str

class RoleOut(RoleBase):
    role_id: int

    class Config:
        form_attributes = True

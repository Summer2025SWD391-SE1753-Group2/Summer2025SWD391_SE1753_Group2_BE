from pydantic import BaseModel, EmailStr
from enum import Enum
from uuid import UUID

class AccountStatusEnum(str, Enum):
    active = "active"
    banned = "banned"
    inactive = "inactive"

class AccountBase(BaseModel):
    username: str
    email: EmailStr
    fullname: str = None
    avatar: str = None
    bio: str = None

class AccountCreate(AccountBase):
    password: str
    role_id: int

class AccountOut(AccountBase):
    account_id: UUID
    status: AccountStatusEnum

    class Config:
        form_attributes = True

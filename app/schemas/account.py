from pydantic import BaseModel, EmailStr
from enum import Enum
from uuid import UUID
from typing import Optional
from datetime import date

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

class AccountCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    date_of_birth: Optional[date] = None

class AccountUpdate(BaseModel):
    phone: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None

class AccountOut(AccountBase):
    account_id: UUID
    status: AccountStatusEnum

    class Config:
        form_attributes = True

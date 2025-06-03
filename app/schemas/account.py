from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from enum import Enum
from uuid import UUID
from typing import Optional
from datetime import date, datetime
from fastapi import HTTPException

from app.core.validators import (
    validate_username,
    validate_password,
    validate_email_address,
    validate_phone_number,
    validate_full_name,
    validate_date_of_birth,
)

class AccountStatusEnum(str, Enum):
    active = "active"
    banned = "banned"
    inactive = "inactive"

class RoleNameEnum(str, Enum):
    user_l1 = "user_l1"
    user_l2 = "user_l2"
    moderator = "moderator"
    admin = "admin"

class RoleOut(BaseModel):
    role_id: int
    role_name: RoleNameEnum
    status: str

    model_config = ConfigDict(from_attributes=True)

class AccountBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=3, max_length=100, example="john_doe")
    email: EmailStr
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        try:
            return validate_username(v)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        try:
            return validate_email_address(v)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        try:
            return validate_full_name(v) if v else v
        except Exception as e:
            raise ValueError(str(e))

class AccountCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, example="khoipd8")
    email: EmailStr = Field(..., example="khoipdse184586@fpt.edu.vn")
    password: str = Field(..., min_length=8, example="SecurePassword@123")
    full_name: Optional[str] = Field(None, min_length=3, max_length=100, example="Phạm Đăng Khôi")
    date_of_birth: Optional[date] = Field(None, example="2004-04-22")
    phone_number: Optional[str] = Field(None, min_length=10, max_length=15, example="0937405359")

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        try:
            # Check if username is unique (you'll need to implement this in your database layer)
            # For now, we'll just validate the format
            return validate_username(v)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        try:
            # Check if password is unique (you'll need to implement this in your database layer)
            # For now, we'll just validate the format
            return validate_password(v)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        try:
            return validate_email_address(v)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        try:
            return validate_full_name(v) if v else v
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("date_of_birth")
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        try:
            return validate_date_of_birth(v) if v else v
        except Exception as e:
            raise ValueError(str(e)) 
        
    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        try:
            # Check if phone number is unique (you'll need to implement this in your database layer)
            # For now, we'll just validate the format
            return validate_phone_number(v) if v else v
        except Exception as e:
            raise ValueError(str(e))

class AccountUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        try:
            return validate_email_address(v) if v else v
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        try:
            return validate_phone_number(v) if v else v
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        try:
            return validate_full_name(v) if v else v
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("date_of_birth")
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        try:
            return validate_date_of_birth(v) if v else v
        except Exception as e:
            raise ValueError(str(e))

class AccountOut(AccountBase):
    account_id: UUID
    status: AccountStatusEnum
    role: RoleOut
    email_verified: bool
    phone_verified: bool
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)

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
    """
    Enum for different account statuses.
    """
    active = "active"
    banned = "banned"
    inactive = "inactive"


class RoleNameEnum(str, Enum):
    """
    Enum for different user roles.
    """
    user = "user"
    moderator = "moderator"
    admin = "admin"


class RoleOut(BaseModel):
    """
    Pydantic model for outputting role information.
    """
    role_id: int
    role_name: RoleNameEnum
    status: str

    model_config = ConfigDict(from_attributes=True)


class AccountBase(BaseModel):
    """
    Base Pydantic model for account information, with common fields and validators.
    """
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=3, max_length=100, example="john_doe")
    email: EmailStr
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username_field(cls, value: str) -> str:
        """
        Validates the username using a custom validator.
        """
        try:
            return validate_username(value)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, value: str) -> str:
        """
        Validates the email address using a custom validator.
        """
        try:
            return validate_email_address(value)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("full_name")
    @classmethod
    def validate_full_name_field(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates the full name using a custom validator, if provided.
        """
        try:
            return validate_full_name(value) if value else value
        except Exception as e:
            raise ValueError(str(e))


class AccountCreate(BaseModel):
    """
    Pydantic model for creating a new account.
    Includes validation for unique fields and password hashing.
    """
    username: str = Field(..., min_length=3, max_length=100, example="khoipd8")
    email: EmailStr = Field(..., example="khoipdse184586@fpt.edu.vn")
    password: str = Field(..., min_length=8, example="SecurePassword@123")
    full_name: Optional[str] = Field(None, min_length=3, max_length=100, example="Pham Dang Khoi")
    date_of_birth: Optional[date] = Field(None, example="2004-04-22")
    # phone_number: Optional[str] = Field(None, min_length=10, max_length=15, example="0937405359")

    @field_validator("username")
    @classmethod
    def validate_username_create(cls, value: str) -> str:
        """
        Validates the username for account creation.
        """
        try:
            return validate_username(value)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("password")
    @classmethod
    def validate_password_create(cls, value: str) -> str:
        """
        Validates the password for account creation.
        """
        try:
            return validate_password(value)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("email")
    @classmethod
    def validate_email_create(cls, value: str) -> str:
        """
        Validates the email for account creation.
        """
        try:
            return validate_email_address(value)
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("full_name")
    @classmethod
    def validate_full_name_create(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates the full name for account creation, if provided.
        """
        try:
            return validate_full_name(value) if value else value
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("date_of_birth")
    @classmethod
    def validate_birth_date_create(cls, value: Optional[date]) -> Optional[date]:
        """
        Validates the date of birth for account creation, if provided.
        """
        try:
            return validate_date_of_birth(value) if value else value
        except Exception as e:
            raise ValueError(str(e))


class AccountUpdate(BaseModel):
    """
    Pydantic model for updating an existing account's profile.
    """
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None

    @field_validator("email")
    @classmethod
    def validate_email_update(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates the email address for account update, if provided.
        """
        try:
            return validate_email_address(value) if value else value
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("phone")
    @classmethod
    def validate_phone_update(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates the phone number for account update, if provided.
        """
        try:
            return validate_phone_number(value) if value else value
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("full_name")
    @classmethod
    def validate_full_name_update(cls, value: Optional[str]) -> Optional[str]:
        """
        Validates the full name for account update, if provided.
        """
        try:
            return validate_full_name(value) if value else value
        except Exception as e:
            raise ValueError(str(e))

    @field_validator("date_of_birth")
    @classmethod
    def validate_birth_date_update(cls, value: Optional[date]) -> Optional[date]:
        """
        Validates the date of birth for account update, if provided.
        """
        try:
            return validate_date_of_birth(value) if value else value
        except Exception as e:
            raise ValueError(str(e))


class AccountOut(AccountBase):
    """
    Pydantic model for outputting full account details.
    """
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


class VerifyPhoneRequest(BaseModel):
    """
    Pydantic model for verifying a phone number with an OTP.
    """
    phone_number: str
    otp: str


class VerifyPhoneResponse(BaseModel):
    """
    Pydantic model for the response after phone verification.
    """
    message: str
    username: str
    role: str


class SendOTPRequest(BaseModel):
    """
    Pydantic model for sending an OTP to a phone number.
    """
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_send_otp(cls, value: str) -> str:
        """
        Validates the phone number format for sending OTP.
        Converts '0xxxxxxxxx' to '+84xxxxxxxxx' if applicable.
        """
        # Convert '0xxxxxxxxx' to '+84xxxxxxxxx'
        if value.startswith("0") and len(value) == 10:
            value = "+84" + value[1:]
        # Validate format: must be +84 followed by 9 digits
        if not (value.startswith("+84") and len(value) == 12 and value[3:].isdigit()):
            raise ValueError("Phone number must be in format +84xxxxxxxxx (9 digits after +84)")
        return value
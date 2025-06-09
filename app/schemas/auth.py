from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum


class MaterialStatusEnum(str, Enum):
    """
    Enum for the status of materials.
    """
    active = "active"
    inactive = "inactive"


# Base schema for common material fields
class MaterialBase(BaseModel):
    """
    Base Pydantic model for material information.
    """
    name: str = Field(..., max_length=150)
    status: MaterialStatusEnum = MaterialStatusEnum.active
    image_url: Optional[str] = Field(None, max_length=500)


# Schema for creating new materials
class MaterialCreate(MaterialBase):
    """
    Pydantic model for creating a new material.
    """
    created_by: Optional[UUID] = None


# Schema for updating existing materials
class MaterialUpdate(BaseModel):
    """
    Pydantic model for updating an existing material.
    """
    name: Optional[str] = Field(None, max_length=150)
    status: Optional[MaterialStatusEnum] = None
    image_url: Optional[str] = Field(None, max_length=500)


# Schema for returning material data
class MaterialOut(MaterialBase):
    """
    Pydantic model for outputting material details.
    """
    material_id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID]
    updated_by: Optional[UUID]

    model_config = ConfigDict(from_attributes=True)


# --- Google OAuth Schemas (Assuming these are in app/schemas/auth.py or similar) ---

class GoogleToken(BaseModel):
    """
    Pydantic model for the response from Google's token endpoint.
    """
    access_token: str
    expires_in: int
    scope: str
    token_type: str
    id_token: Optional[str] = None
    refresh_token: Optional[str] = None


class GoogleUserInfo(BaseModel):
    """
    Pydantic model for user information retrieved from Google's userinfo endpoint.
    """
    id: str
    email: EmailStr
    verified_email: bool
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
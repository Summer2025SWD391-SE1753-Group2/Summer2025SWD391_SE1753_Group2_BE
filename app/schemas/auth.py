from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from enum import Enum


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
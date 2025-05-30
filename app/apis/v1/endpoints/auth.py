from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.settings import settings
from app.schemas.token import Token, TokenData
from app.services.token_service import TokenService

router = APIRouter()

JWT_SECRET_KEY=settings.JWT_SECRET_KEY
JWT_ALGORITHM=settings.JWT_ALGORITHM

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

@router.post("/access-token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Verify user credentials here
    # If valid, create tokens
    token_data = {
        "sub": form_data.username,
        "user_id": 1  # Replace with actual user ID
    }
    
    access_token = TokenService.create_access_token(token_data)
    refresh_token = TokenService.create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh-token")
async def refresh_token(refresh_token: str):
    payload = TokenService.verify_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new access token
    token_data = {
        "sub": payload.get("sub"),
        "user_id": payload.get("user_id")
    }
    new_access_token = TokenService.create_access_token(token_data)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

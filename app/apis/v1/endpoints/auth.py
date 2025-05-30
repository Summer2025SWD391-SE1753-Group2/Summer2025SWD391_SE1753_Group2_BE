from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Security
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.settings import settings
from app.schemas.token import Token, TokenData
from app.services.token_service import TokenService

router = APIRouter()

JWT_SECRET_KEY=settings.JWT_SECRET_KEY
JWT_ALGORITHM=settings.JWT_ALGORITHM

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Update OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/access-token",
    scopes={
        "me": "Read information about the current user.",
        "items": "Read items."
    }
)

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> TokenData:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    payload = TokenService.verify_token(token)
    if payload is None:
        raise credentials_exception
    
    token_data = TokenData(
        username=payload.get("sub"),
        user_id=payload.get("user_id"),
        exp=payload.get("exp")
    )
    
    if token_data is None:
        raise credentials_exception
    
    for scope in security_scopes.scopes:
        if scope not in payload.get("scopes", []):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return token_data

@router.post("/access-token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Verify user credentials here
    # If valid, create tokens
    token_data = {
        "sub": form_data.username,
        "user_id": 1,  # Replace with actual user ID
        "scopes": form_data.scopes
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
        "user_id": payload.get("user_id"),
        "scopes": payload.get("scopes", [])
    }
    new_access_token = TokenService.create_access_token(token_data)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

# Example of a protected route
@router.get("/users/me", response_model=TokenData)
async def read_users_me(
    current_user: TokenData = Security(get_current_user, scopes=["me"])
):
    return current_user

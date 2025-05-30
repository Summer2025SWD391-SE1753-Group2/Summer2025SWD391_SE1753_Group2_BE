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
from app.core.deps import get_db
from app.db.models.account import Account, AccountStatusEnum

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

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(Account).filter(Account.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    if user.status != AccountStatusEnum.active:
        return False
    return user

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
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
    
    try:
        # Verify token in database
        token_record = TokenService.get_active_token(db, token)
        if not token_record:
            raise credentials_exception

        # Verify JWT token
        payload = TokenService.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user = db.query(Account).filter(Account.username == username).first()
        if user is None or user.status != AccountStatusEnum.active:
            raise credentials_exception
        
        token_data = TokenData(
            username=username,
            user_id=str(user.account_id),
            exp=payload.get("exp")
        )
        
        for scope in security_scopes.scopes:
            if scope not in payload.get("scopes", []):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        
        return token_data
    except JWTError:
        raise credentials_exception

@router.post("/access-token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = {
        "sub": user.username,
        "user_id": str(user.account_id),
        "scopes": form_data.scopes
    }
    
    access_token = TokenService.create_access_token(token_data)
    refresh_token = TokenService.create_refresh_token(token_data)
    
    # Create token record in database
    token_record = TokenService.create_token_record(db, user, access_token, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh-token")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    try:
        payload = TokenService.verify_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data"
            )
        
        user = db.query(Account).filter(Account.username == username).first()
        if user is None or user.status != AccountStatusEnum.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        token_data = {
            "sub": user.username,
            "user_id": str(user.account_id),
            "scopes": payload.get("scopes", [])
        }
        new_access_token = TokenService.create_access_token(token_data)
        
        # Create new token record
        token_record = TokenService.create_token_record(db, user, new_access_token)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

# Example of a protected route
@router.get("/users/me", response_model=TokenData)
async def read_users_me(
    current_user: TokenData = Security(get_current_user, scopes=["me"])
):
    return current_user

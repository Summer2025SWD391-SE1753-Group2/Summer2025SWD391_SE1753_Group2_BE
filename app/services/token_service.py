from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt
from sqlalchemy.orm import Session
from app.core.settings import settings
from app.db.models.token import Token
from app.db.models.account import Account
import uuid

class TokenService:
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.JWTError:
            return None

    @staticmethod
    def create_token_record(db: Session, account: Account, access_token: str, refresh_token: str = None) -> Token:
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Deactivate all existing tokens for this account
        db.query(Token).filter(
            Token.account_id == account.account_id,
            Token.is_active == True
        ).update({"is_active": False})
        
        # Create new token record
        token = Token(
            account_id=account.account_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return token

    @staticmethod
    def get_active_token(db: Session, access_token: str) -> Optional[Token]:
        return db.query(Token).filter(
            Token.access_token == access_token,
            Token.is_active == True,
            Token.expires_at > datetime.now(timezone.utc)
        ).first()

    @staticmethod
    def deactivate_token(db: Session, token_id: uuid.UUID):
        db.query(Token).filter(Token.token_id == token_id).update({"is_active": False})
        db.commit()
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.settings import settings
from app.db.models.token import Token
from app.db.models.account import Account
import uuid

class TokenService:
    """
    Service class for handling JWT token creation, verification, and database management.
    """

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates a new JWT access token.

        Args:
            data (dict): The payload to encode into the token.
            expires_delta (Optional[timedelta]): The timedelta for token expiration.
                                                 Defaults to ACCESS_TOKEN_EXPIRE_MINUTES from settings.

        Returns:
            str: The encoded JWT access token.
        """
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
        """
        Creates a new JWT refresh token.

        Args:
            data (dict): The payload to encode into the token.

        Returns:
            str: The encoded JWT refresh token.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verifies a JWT token and returns its payload if valid.

        Args:
            token (str): The JWT token string.

        Returns:
            Optional[dict]: The decoded token payload if valid, otherwise None.
        """
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            # This handles both ExpiredSignatureError and InvalidTokenError
            return None

    @staticmethod
    def create_token_record(db: Session, account: Account, access_token: str, refresh_token: Optional[str] = None) -> Token:
        """
        Creates a new token record in the database, deactivating previous active tokens for the account.

        Args:
            db (Session): The database session.
            account (Account): The account associated with the token.
            access_token (str): The access token string.
            refresh_token (Optional[str]): The refresh token string (optional).

        Returns:
            Token: The newly created database token record.
        """
        # Calculate expiration time for the database record
        # This should align with the JWT's 'exp' claim for the access_token
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        # Deactivate all existing active tokens for this account to enforce single active session
        db.query(Token).filter(
            Token.account_id == account.account_id,
            Token.is_active == True
        ).update({"is_active": False}, synchronize_session=False) # Use synchronize_session=False for bulk updates

        # Create new token record
        token_record = Token(
            account_id=account.account_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            is_active=True # Explicitly set as active
        )
        db.add(token_record)
        db.commit()
        db.refresh(token_record)
        return token_record

    @staticmethod
    def get_active_token(db: Session, access_token: str) -> Optional[Token]:
        """
        Retrieves an active and unexpired token record from the database.

        Args:
            db (Session): The database session.
            access_token (str): The access token string.

        Returns:
            Optional[Token]: The active token record if found, otherwise None.
        """
        return db.query(Token).filter(
            Token.access_token == access_token,
            Token.is_active == True,
            Token.expires_at > datetime.now(timezone.utc)
        ).first()

    @staticmethod
    def deactivate_token(db: Session, token_id: uuid.UUID):
        """
        Deactivates a specific token record in the database, effectively revoking it.

        Args:
            db (Session): The database session.
            token_id (uuid.UUID): The UUID of the token record to deactivate.
        """
        db.query(Token).filter(Token.token_id == token_id).update(
            {"is_active": False, "revoked_at": datetime.now(timezone.utc)},
            synchronize_session=False # Use synchronize_session=False for bulk updates
        )
        db.commit()
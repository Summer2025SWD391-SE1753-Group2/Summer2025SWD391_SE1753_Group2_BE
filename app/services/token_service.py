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
            is_active=True, # Explicitly set as active
            token_type="access"  # Explicitly set type
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

    @staticmethod
    def create_reset_password_token_record(db: Session, account: Account, reset_token: str, expires_at: datetime) -> Token:
        """
        Lưu token reset password vào DB.
        Deactivate tất cả reset_password tokens cũ để chỉ có 1 token active tại 1 thời điểm.
        """
        
        # Deactivate tất cả reset_password tokens cũ của user này
        db.query(Token).filter(
            Token.account_id == account.account_id,
            Token.is_active == True,
            Token.token_type == "reset_password"  # CHỈ deactivate reset_password tokens
        ).update({"is_active": False}, synchronize_session=False)
        
        # Tạo token record mới
        token_record = Token(
            account_id=account.account_id,
            access_token=reset_token,
            refresh_token=None,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at,
            token_type="reset_password"
        )
        db.add(token_record)
        db.commit()
        db.refresh(token_record)
        
        print(f"✅ Created reset_password token for user {account.username}")
        print(f"   Token ID: {token_record.token_id}")
        print(f"   Expires at: {expires_at}")
        
        return token_record

    # BONUS: Thêm method cleanup expired tokens
    @staticmethod
    def cleanup_expired_tokens(db: Session):
        """
        Cleanup các tokens đã hết hạn để giữ database sạch sẽ
        """
        current_time = datetime.now(timezone.utc)
        
        # Deactivate expired tokens
        expired_count = db.query(Token).filter(
            Token.is_active == True,
            Token.expires_at < current_time
        ).update({"is_active": False}, synchronize_session=False)
        
        db.commit()
        
        if expired_count > 0:
            print(f"🧹 Cleaned up {expired_count} expired tokens")
        
        return expired_count

    # BONUS: Method để revoke tất cả tokens của user (dùng khi ban user)
    @staticmethod  
    def revoke_all_user_tokens(db: Session, account_id: uuid.UUID):
        """
        Revoke tất cả tokens của user (dùng khi ban account)
        """
        revoked_count = db.query(Token).filter(
            Token.account_id == account_id,
            Token.is_active == True
        ).update({"is_active": False}, synchronize_session=False)
        
        db.commit()
        
        print(f"🚫 Revoked {revoked_count} tokens for user {account_id}")
        return revoked_count

    # BONUS: Method để get token statistics
    @staticmethod
    def get_user_token_stats(db: Session, account_id: uuid.UUID):
        """
        Lấy thống kê tokens của user để debug
        """
        tokens = db.query(Token).filter(Token.account_id == account_id).all()
        
        stats = {
            "total": len(tokens),
            "active": len([t for t in tokens if t.is_active]),
            "by_type": {},
            "expired": 0
        }
        
        current_time = datetime.now(timezone.utc)
        
        for token in tokens:
            # Count by type
            token_type = token.token_type
            if token_type not in stats["by_type"]:
                stats["by_type"][token_type] = {"total": 0, "active": 0}
            
            stats["by_type"][token_type]["total"] += 1
            if token.is_active:
                stats["by_type"][token_type]["active"] += 1
            
            # Count expired
            if token.expires_at and token.expires_at < current_time:
                stats["expired"] += 1
        
        return stats
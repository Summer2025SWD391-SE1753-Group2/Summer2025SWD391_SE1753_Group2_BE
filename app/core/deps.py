from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.database import SessionLocal
from app.db.models.account import Account
from app.core.settings import settings
from app.schemas.account import AccountStatusEnum
from app.db.models.role import RoleNameEnum

# Configure OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/access-token",
    scopes={
        "me": "Read information about the current user.",
        "items": "Read items."
    }
)

# 1. Dependency mở session DB
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 2. Giải mã JWT, tìm account trong DB
def get_current_account(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Account:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    account = db.query(Account).filter(Account.username == username).first()
    if account is None or account.status != AccountStatusEnum.active:
        raise credentials_exception

    return account


# 3. Yêu cầu account đã đăng nhập (User, Moderator, Admin)
def get_current_active_account(current_account: Account = Depends(get_current_account)):
    if current_account.role.role_name not in [RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires User account or above"
        )
    return current_account


# 5. Yêu cầu Moderator
def get_current_moderator(current_account: Account = Depends(get_current_account)):
    if current_account.role.role_name not in [RoleNameEnum.moderator, RoleNameEnum.admin]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator access only"
        )
    return current_account


# 6. Yêu cầu Admin
def get_current_admin(current_account: Account = Depends(get_current_account)):
    if current_account.role.role_name != RoleNameEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )
    return current_account

from typing import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.database import SessionLocal
from app.db.models.account import Account
from app.core.settings import settings
from app.schemas.account import AccountStatusEnum
from app.db.models.role import RoleNameEnum


# 1. Dependency mở session DB
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 2. Giải mã JWT, tìm account trong DB
def get_current_account(db: Session = Depends(get_db), token: str = Depends(...)):
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
        account_id: str = payload.get("sub")
        if account_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    account = db.query(Account).filter(Account.account_id == account_id).first()
    if account is None or account.status != AccountStatusEnum.active:
        raise credentials_exception

    return account


# 3. Yêu cầu account đã đăng nhập & là L1
def get_current_active_account_l1(current_account: Account = Depends(get_current_account)):
    if current_account.role.role_name not in [RoleNameEnum.account_l1, RoleNameEnum.account_l2, RoleNameEnum.moderator, RoleNameEnum.admin]:
        raise HTTPException(status_code=403, detail="Requires Level 1 account or above")
    return current_account


# 4. Yêu cầu L2
def get_current_active_account_l2(current_account: Account = Depends(get_current_account)):
    if current_account.role.role_name not in [RoleNameEnum.account_l2, RoleNameEnum.moderator, RoleNameEnum.admin]:
        raise HTTPException(status_code=403, detail="Requires Level 2 account or above")
    return current_account


# 5. Yêu cầu Moderator
def get_current_moderator(current_account: Account = Depends(get_current_account)):
    if current_account.role.role_name not in [RoleNameEnum.moderator, RoleNameEnum.admin]:
        raise HTTPException(status_code=403, detail="Moderator access only")
    return current_account


# 6. Yêu cầu Admin
def get_current_admin(current_account: Account = Depends(get_current_account)):
    if current_account.role.role_name != RoleNameEnum.admin:
        raise HTTPException(status_code=403, detail="Admin access only")
    return current_account

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.db.models.account import Account
from app.core.settings import settings
from app.core.deps import get_db
from typing import List
from app.schemas.account import RoleNameEnum
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Optional[Account]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        # Use user_id instead of sub
        account_id = payload.get("user_id")
        if account_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    user = db.query(Account).filter(Account.account_id == account_id).first()
    if user is None:
        raise credentials_exception
        
    return user
def check_roles(allowed_roles: List[RoleNameEnum]):
    async def role_checker(current_user: Account = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Chưa đăng nhập"
            )
        
        if current_user.role.role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền thực hiện hành động này"
            )
        return current_user
    return role_checker
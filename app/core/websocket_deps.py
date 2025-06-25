from fastapi import WebSocket, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.database import SessionLocal
from app.db.models.account import Account
from app.core.settings import settings
from app.schemas.account import AccountStatusEnum

async def get_current_user_websocket(websocket: WebSocket) -> Account:
    """Authenticate user for WebSocket connection"""
    try:
        # Get token from query parameters
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
            raise HTTPException(status_code=401, detail="Missing authentication token")
        
        # Decode JWT token
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            username: str = payload.get("sub")
            if username is None:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
                raise HTTPException(status_code=401, detail="Invalid token")
        except JWTError:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        db = SessionLocal()
        try:
            account = db.query(Account).filter(
                Account.username == username,
                Account.status == AccountStatusEnum.active
            ).first()
            
            if account is None:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found or inactive")
                raise HTTPException(status_code=401, detail="User not found or inactive")
            
            return account
        finally:
            db.close()
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Authentication failed")
        raise HTTPException(status_code=500, detail="Authentication failed") 
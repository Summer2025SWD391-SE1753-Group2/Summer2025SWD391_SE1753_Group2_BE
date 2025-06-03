import httpx
from fastapi import HTTPException
from app.core.settings import settings
from app.schemas.auth import GoogleToken, GoogleUserInfo
from app.db.models.account import Account, AccountStatusEnum
from sqlalchemy.orm import Session
from app.services.token_service import TokenService
from app.core.security import get_password_hash
import uuid
from datetime import datetime

async def get_google_token(code: str) -> GoogleToken:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI
            }
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to get Google token"
            )
        return GoogleToken(**response.json())

async def get_google_user_info(access_token: str) -> GoogleUserInfo:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Failed to get Google user info"
            )
        return GoogleUserInfo(**response.json())

async def get_or_create_google_account(db: Session, google_user: GoogleUserInfo) -> Account:
    # Check if account exists
    account = db.query(Account).filter(Account.email == google_user.email).first()
    
    if account:
        if account.status != AccountStatusEnum.active:
            raise HTTPException(
                status_code=400,
                detail="Account is not active"
            )
        return account
    
    # Create new account
    username = f"google_{google_user.id}"
    account = Account(
        username=username,
        email=google_user.email,
        password_hash=get_password_hash(str(uuid.uuid4())),  # Random password
        full_name=google_user.name,
        avatar=google_user.picture,
        status=AccountStatusEnum.active,
        email_verified=True,  # Google email is already verified
        role_id=1,  # Default role: user_l1
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    
    # Update created_by and updated_by
    account.created_by = account.account_id
    account.updated_by = account.account_id
    db.commit()
    db.refresh(account)
    
    return account 
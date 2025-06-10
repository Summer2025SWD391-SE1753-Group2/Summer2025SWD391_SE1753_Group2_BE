import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.core.settings import settings
from app.schemas.auth import GoogleToken, GoogleUserInfo # Corrected import path based on schema changes
from app.db.models.account import Account, AccountStatusEnum
from app.core.security import get_password_hash # Assuming this is the correct import for password hashing

# Assuming TokenService is imported and has relevant methods, though not directly used here
# from app.services.token_service import TokenService

async def get_google_token(code: str) -> GoogleToken:
    """
    Exchanges an authorization code for Google OAuth tokens.
    """
    try:
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
            response.raise_for_status() # Raises an HTTPStatusError for bad responses (4xx or 5xx)
            return GoogleToken(**response.json())
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to get Google token: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while getting Google token: {str(e)}"
        )


async def get_google_user_info(access_token: str) -> GoogleUserInfo:
    """
    Retrieves user information from Google using an access token.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status() # Raises an HTTPStatusError for bad responses (4xx or 5xx)
            return GoogleUserInfo(**response.json())
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to get Google user info: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while getting Google user info: {str(e)}"
        )


async def get_or_create_google_account(db: Session, google_user: GoogleUserInfo) -> Account:
    """
    Retrieves an existing account by email or creates a new one for Google users.
    """
    # Check if an account with this email already exists
    account = db.query(Account).filter(Account.email == google_user.email).first()

    if account:
        # If account exists, check its status
        if account.status != AccountStatusEnum.active:
            raise HTTPException(
                status_code=400,
                detail="Existing account linked to this email is not active."
            )
        return account

    # If no account exists, create a new one for the Google user
    # Generate a unique username by prepending "google_" to the Google ID
    # This prevents username conflicts with existing local accounts.
    username = f"google_{google_user.id}"
    # Ensure username is unique - add a loop or more robust strategy if collisions are possible
    # For simplicity, assuming google_user.id is unique enough for initial username.
    # In a real app, you might want to check for username uniqueness and append numbers if needed.

    # Create a random password hash since Google handles authentication
    random_password_hash = get_password_hash(str(uuid.uuid4()))

    new_account = Account(
        username=username,
        email=google_user.email,
        password_hash=random_password_hash,
        full_name=google_user.name,
        avatar=google_user.picture,
        status=AccountStatusEnum.active, # New social accounts are active by default
        email_verified=True,  # Google verifies email addresses
        role_id=1,  # Default role for new users
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    # Set created_by and updated_by to the new account's ID
    new_account.created_by = new_account.account_id
    new_account.updated_by = new_account.account_id
    db.commit()
    db.refresh(new_account)

    return new_account
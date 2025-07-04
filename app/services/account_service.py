from sqlalchemy.orm import Session
from app.db.models.account import Account, AccountStatusEnum
from app.schemas.account import AccountCreate, AccountUpdate
from app.core.security import get_password_hash, verify_password
from fastapi import HTTPException
from sqlalchemy import text
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from app.services.email_service import send_confirmation_email, send_email_verification
from jose import jwt, JWTError
from app.core.settings import settings
from datetime import datetime


def check_unique_fields(db: Session, username: Optional[str] = None, email: Optional[str] = None, phone_number: Optional[str] = None):
    """
    Checks if username, email, or phone number already exist in the database.
    Raises HTTPException if a duplicate is found.
    """
    if username:
        existing_username = db.execute(
            text("SELECT 1 FROM account WHERE username = :username"),
            {"username": username}
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

    if email:
        existing_email = db.execute(
            text("SELECT 1 FROM account WHERE email = :email"),
            {"email": email}
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )

    if phone_number:
        existing_phone = db.execute(
            text("SELECT 1 FROM account WHERE phone_number = :phone_number"),
            {"phone_number": phone_number}
        ).first()
        if existing_phone:
            raise HTTPException(
                status_code=400,
                detail="Phone number already exists"
            )


def search_accounts_by_name(
    db: Session,
    name: str,
    skip: int = 0,
    limit: int = 100
) -> List[Account]:
    """
    Searches for accounts by username using a case-insensitive partial match.
    Only active accounts are returned.
    """
    return db.query(Account) \
        .filter(
            (Account.username.ilike(f"%{name}%"))
        ) \
        .filter(Account.status == AccountStatusEnum.active) \
        .offset(skip) \
        .limit(limit) \
        .all()


async def create_account(db: Session, account: AccountCreate) -> Account:
    """
    Creates a new account in the database.
    Performs unique field checks, hashes the password, sets initial status,
    and sends a confirmation email.
    """
    try:
        # Check unique constraints before creating
        check_unique_fields(db, username=account.username, email=account.email)

        hashed_password = get_password_hash(account.password)

        db_account = Account(
            username=account.username,
            email=account.email,
            password_hash=hashed_password,
            full_name=account.full_name,
            date_of_birth=account.date_of_birth,
            phone_number=None,
            phone_verified=False,  # Always set to False initially
            role_id=1,  # Always set to user initially
            status=AccountStatusEnum.inactive,  # Default status: inactive
            avatar="https://img.freepik.com/premium-vector/person-with-blue-shirt-that-says-name-person_1029948-7040.jpg",
            bio="Welcome to my profile!",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            created_by=None,
            updated_by=None
        )

        db.add(db_account)
        db.commit()
        db.refresh(db_account)

        # Update created_by and updated_by to the new account_id
        db_account.created_by = db_account.account_id
        db_account.updated_by = db_account.account_id
        db.commit()
        db.refresh(db_account)

        # Send confirmation email
        await send_confirmation_email(db_account.email, db_account.username)

        return db_account

    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        if "account_username_key" in error_msg:
            raise HTTPException(status_code=400, detail="Username already exists")
        elif "account_email_key" in error_msg:
            raise HTTPException(status_code=400, detail="Email already exists")
        elif "account_phone_number_key" in error_msg:
            raise HTTPException(status_code=400, detail="Phone number already exists")
        raise HTTPException(status_code=400, detail="Registration failed due to duplicate data")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


async def confirm_email(db: Session, token: str) -> Account:
    """
    Confirms a user's email address using a JWT token.
    Activates the account and sets email_verified to True upon successful confirmation.
    """
    try:
        # Verify token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid token"
            )

        # Get account
        account = db.query(Account).filter(Account.username == username).first()
        if account is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        # Update status and email_verified
        account.status = AccountStatusEnum.active
        account.email_verified = True
        db.commit()
        db.refresh(account)

        return account
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )


async def update_account_profile(db: Session, account: Account, profile_update: AccountUpdate) -> Account:
    """
    Updates an existing account's profile information.
    Handles email and phone number updates, including sending verification emails
    and setting verification status to False if changed.
    """
    try:
        # If email is being updated, send verification email
        if profile_update.email and profile_update.email != account.email:
            # Check if new email is already in use
            existing_email = db.query(Account).filter(
                Account.email == profile_update.email,
                Account.account_id != account.account_id
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=400,
                    detail="Email already in use"
                )
            # Send verification email
            await send_email_verification(account.email, account.username, profile_update.email)
            # Set email_verified to False until verified
            account.email_verified = False
            account.email = profile_update.email # Update email in account object

        # If phone number is being updated, set phone_verified to False
        if profile_update.phone and profile_update.phone != account.phone_number:
            # Check if new phone number is already in use
            existing_phone = db.query(Account).filter(
                Account.phone_number == profile_update.phone,
                Account.account_id != account.account_id
            ).first()
            if existing_phone:
                raise HTTPException(
                    status_code=400,
                    detail="Phone number already in use"
                )
            account.phone_number = profile_update.phone
            account.phone_verified = False

        # Update other fields
        if profile_update.full_name is not None:
            account.full_name = profile_update.full_name
        if profile_update.date_of_birth is not None:
            account.date_of_birth = profile_update.date_of_birth

        account.updated_at = datetime.now() # Update the updated_at timestamp

        db.commit()
        db.refresh(account)
        return account

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def update_password(db: Session, account: Account, new_password: str, current_password: Optional[str] = None) -> Account:
    """
    Updates an account's password.
    For Google users, current_password is optional.
    For regular users, current_password is required.
    """
    try:
        # For non-Google users, verify current password
        if not account.username.startswith("google_") and current_password:
            if not verify_password(current_password, account.password_hash):
                raise HTTPException(
                    status_code=400,
                    detail="Current password is incorrect"
                )
        
        # Hash and update the new password
        hashed_password = get_password_hash(new_password)
        account.password_hash = hashed_password
        account.updated_at = datetime.now()
        
        db.commit()
        db.refresh(account)
        return account
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def update_username(db: Session, account: Account, new_username: str) -> Account:
    """
    Updates an account's username.
    Checks for uniqueness and handles Google user username updates.
    """
    try:
        # Check if new username is already in use
        existing_username = db.query(Account).filter(
            Account.username == new_username,
            Account.account_id != account.account_id
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already in use"
            )
        
        # Update username
        account.username = new_username
        account.updated_at = datetime.now()
        
        db.commit()
        db.refresh(account)
        return account
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


def is_google_user(account: Account) -> bool:
    """
    Checks if an account was created via Google OAuth.
    """
    return account.username.startswith("google_")
def get_account(db: Session, account_id: str) -> Account:
    """
    Get account by account_id.
    Raises HTTPException if not found.
    """
    account = db.query(Account).filter(Account.account_id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

async def get_account_profile(db: Session, username: str) -> Account:
    """
    Retrieves an account's profile by username.
    Raises HTTPException if the account is not found or is not active.
    """
    account = db.query(Account).filter(Account.username == username).first()
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if account.status != AccountStatusEnum.active:
        raise HTTPException(
            status_code=400,
            detail="Account is not active"
        )

    return account

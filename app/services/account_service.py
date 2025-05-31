from sqlalchemy.orm import Session
from app.db.models.account import Account, AccountStatusEnum
from app.schemas.account import AccountCreate, AccountUpdate
from app.core.security import get_password_hash
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.services.email_service import send_confirmation_email, send_email_verification
from jose import jwt, JWTError
from app.core.settings import settings

def check_unique_fields(db: Session, username: str = None, email: str = None):
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

async def create_account(db: Session, account: AccountCreate) -> Account:
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
            phone_number=account.phone_number,
            phone_verified=False,  # Always set to False initially
            role_id=1,  # Always set to user_l1 initially
            status=AccountStatusEnum.inactive,  # Default status: inactive
            avatar=None,
            bio=None,
        )

        db.add(db_account)
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

        db.commit()
        db.refresh(account)
        return account

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

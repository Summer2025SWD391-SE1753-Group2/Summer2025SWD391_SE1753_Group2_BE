from sqlalchemy.orm import Session
from app.db.models.account import Account
from app.schemas.account import AccountCreate
from app.core.security import get_password_hash
from app.db.models.account import AccountStatusEnum
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

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

def create_account(db: Session, account: AccountCreate) -> Account:
    try:
        # Check unique constraints before creating
        check_unique_fields(db, username=account.username, email=account.email)
        
        hashed_password = get_password_hash(account.password)
        
        db_account = Account(
            username=account.username,
            email=account.email,
            password_hash=hashed_password,  # Changed to match the model's field name
            full_name=account.full_name,
            date_of_birth=account.date_of_birth,
            role_id=1,
            status=AccountStatusEnum.active,
            avatar=None,
            bio=None,
        )

        db.add(db_account)
        db.commit()
        db.refresh(db_account)
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

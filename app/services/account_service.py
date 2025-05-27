from sqlalchemy.orm import Session
from app.db.models.account import Account
from app.schemas.account import AccountCreate
from app.core.security import get_password_hash

def create_account(db: Session, account: AccountCreate):
    hashed_password = get_password_hash(account.password)
    db_account = Account(
        username=account.username,
        email=account.email,
        password_hash=hashed_password,
        fullname=account.fullname,
        bio=account.bio,
        role_id=account.role_id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

from sqlalchemy.orm import Session
from app.db.models.account import Account
from app.schemas.account import AccountCreate
from app.core.security import get_password_hash
from app.db.models.account import AccountStatusEnum

def create_account(db: Session, account: AccountCreate) -> Account:
    hashed_password = get_password_hash(account.password)

    db_account = Account(
        username=account.username,
        email=account.email,
        password_hash=hashed_password,  # Changed to match the model's field name
        fullname=account.full_name,     # Also notice it's fullname not full_name
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

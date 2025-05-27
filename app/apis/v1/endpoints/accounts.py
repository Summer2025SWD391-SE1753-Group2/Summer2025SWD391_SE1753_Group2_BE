from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.account import AccountCreate, AccountOut
from app.services.account_service import create_account
from app.core.deps import get_db

router = APIRouter()

@router.post("/", response_model=AccountOut)
def register_account(account: AccountCreate, db: Session = Depends(get_db)):
    return create_account(db, account)

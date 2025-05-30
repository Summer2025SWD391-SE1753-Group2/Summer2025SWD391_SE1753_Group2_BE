from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.schemas.account import AccountCreate, AccountOut
from app.services.account_service import create_account, confirm_email
from app.core.deps import get_db
from app.db.models.account import AccountStatusEnum

router = APIRouter()

@router.post("/", response_model=AccountOut)
async def register_account(account: AccountCreate, db: Session = Depends(get_db)):
    return await create_account(db, account)

@router.get("/confirm-email")
async def confirm_email_endpoint(token: str = Query(...), db: Session = Depends(get_db)):
    try:
        account = await confirm_email(db, token)
        return {
            "message": "Email confirmed successfully",
            "account": {
                "username": account.username,
                "email": account.email,
                "status": account.status.value
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to confirm email: {str(e)}"
        )

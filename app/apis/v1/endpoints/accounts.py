from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.schemas.account import AccountCreate, AccountOut, AccountUpdate
from app.services.account_service import create_account, confirm_email, update_account_profile, send_confirmation_email
from app.core.deps import get_db, get_current_active_account_l1
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

@router.put("/profile", response_model=AccountOut)
async def update_profile(
    profile_update: AccountUpdate,
    current_account = Depends(get_current_active_account_l1),
    db: Session = Depends(get_db)
):
    return await update_account_profile(db, current_account, profile_update)

@router.post("/resend-confirmation")
async def resend_confirmation_email(username: str = Query(...), db: Session = Depends(get_db)):
    try:
        # Find account
        account = db.query(Account).filter(Account.username == username).first()
        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )
        
        if account.email_verified:
            raise HTTPException(
                status_code=400,
                detail="Email already verified"
            )
        
        # Send confirmation email
        await send_confirmation_email(account.email, account.username)
        
        return {
            "message": "Confirmation email sent successfully",
            "username": account.username,
            "email": account.email
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to send confirmation email: {str(e)}"
        )

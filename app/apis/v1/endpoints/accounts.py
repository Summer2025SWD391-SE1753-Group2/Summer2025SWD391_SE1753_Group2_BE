from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.account import AccountOut, AccountUpdate
from app.services.account_service import search_accounts_by_name,confirm_email, update_account_profile, send_confirmation_email, get_account_profile
from app.core.deps import get_db, get_current_active_account_l1
from app.db.models.account import Account, AccountStatusEnum

router = APIRouter()

@router.get("/confirm-email")
async def confirm_email_get(token: str = Query(...), db: Session = Depends(get_db)):
    """
    Confirm email with token (GET method)
    """
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

@router.post("/confirm-email")
async def confirm_email_post(token: str = Query(...), db: Session = Depends(get_db)):
    """
    Confirm email with token (POST method)
    """
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
@router.get("/search/", response_model=List[AccountOut])
def search_accounts_endpoint(
    name: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_account_l1)
):
    """
    Search accounts by username or full name
    """
    return search_accounts_by_name(db, name, skip=skip, limit=limit)
@router.post("/resend-confirmation")
async def resend_confirmation_email(username: str, db: Session = Depends(get_db)):
    """
    Resend confirmation email
    """
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
    await send_confirmation_email(account.email, account.username)
    return {"message": "Confirmation email sent"}

@router.put("/me", response_model=AccountOut)
async def update_profile(
    profile_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_active_account_l1)
):
    """
    Update current account profile
    """
    return await update_account_profile(db, current_account, profile_update)

@router.get("/me", response_model=AccountOut)
async def view_own_profile(
    current_account: Account = Depends(get_current_active_account_l1)
):
    """
    View own profile
    """
    return current_account

@router.get("/profiles/{username}", response_model=AccountOut)
async def view_profile(
    username: str,
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_active_account_l1)
):
    """
    View profile of a specific account
    """
    return await get_account_profile(db, username)

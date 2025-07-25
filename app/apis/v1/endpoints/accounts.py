from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.account import AccountOut, AccountUpdate, AccountCreate, RoleNameEnum, PasswordUpdateRequest, UsernameUpdateRequest
from app.services.account_service import search_accounts_by_name, confirm_email, update_account_profile, send_confirmation_email, get_account_profile, update_password, update_username, is_google_user
from app.core.deps import get_db, get_current_active_account
from app.db.models.account import Account, AccountStatusEnum
from app.services import account_service
from app.apis.v1.endpoints.check_role import check_roles
from fastapi.responses import RedirectResponse
from app.core import settings

router = APIRouter()

DEFAULT_FE_URL = 'http://localhost:5173'

@router.get("/confirm-email")
async def confirm_email_get(token: str = Query(...), db: Session = Depends(get_db)):
    """
    Confirm email with token (GET method)
    """
    try:
        await confirm_email(db, token)
        # Redirect về FE /verify-success
        frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FE_URL)
        redirect_url = f"{frontend_url}/verify-success"
        return RedirectResponse(url=redirect_url)
    except HTTPException as e:
        frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FE_URL)
        redirect_url = f"{frontend_url}/verify-failed"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FE_URL)
        redirect_url = f"{frontend_url}/verify-failed"
        return RedirectResponse(url=redirect_url)

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
    current_user: Account = Depends(get_current_active_account)
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

@router.post("/", response_model=AccountOut)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user account
    """
    return account_service.create_account(db=db, account=account)

@router.post("/moderator", response_model=AccountOut)
def create_moderator(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """
    Create a new moderator account
    Only admin can create moderator accounts
    """
    # Set role to moderator
    account.role_name = RoleNameEnum.moderator
    return account_service.create_account(db=db, account=account)

@router.get("/me", response_model=AccountOut)
def read_account_me(
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Get current account information
    """
    return current_account

@router.get("/is-google-user")
def check_google_user(
    current_account: Account = Depends(get_current_active_account)
):
    """
    Check if current user is a Google user
    """
    return {
        "is_google_user": is_google_user(current_account),
        "username": current_account.username,
        "email": current_account.email
    }

@router.put("/me", response_model=AccountOut)
def update_account_me(
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Update current account information
    """
    return account_service.update_account(
        db=db,
        account_id=current_account.account_id,
        account_update=account_update
    )
@router.get("/all", response_model=List[AccountOut])
def get_all_accounts(
    status: Optional[AccountStatusEnum] = Query(None, description="Filter by account status (active, banned, inactive)"),
    skip: int = Query(0, ge=0, description="Number of accounts to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of accounts to return"),
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Get all accounts, optionally filter by status"""
    query = db.query(Account)
    if status:
        query = query.filter(Account.status == status)
    accounts = query.offset(skip).limit(limit).all()
    return accounts
@router.get("/{account_id}", response_model=AccountOut)
def read_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Get account by ID
    Only moderator and admin can view other accounts
    """
    db_account = account_service.get_account(db=db, account_id=account_id)
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return db_account

@router.put("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: str,
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """
    Update account information
    Only admin can update other accounts
    """
    return account_service.update_account(
        db=db,
        account_id=account_id,
        account_update=account_update
    )

@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """
    Delete account
    Only admin can delete accounts
    """
    account_service.delete_account(db=db, account_id=account_id)

@router.get("/profiles/{username}", response_model=AccountOut)
async def view_profile(
    username: str,
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_active_account)
):
    """
    View profile of a specific account
    """
    return await get_account_profile(db, username)

@router.post("/update-password", response_model=AccountOut)
def update_password_endpoint(
    password_update: PasswordUpdateRequest,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Update password for current user
    For Google users, current_password is optional
    For regular users, current_password is required
    """
    return update_password(
        db=db, 
        account=current_account, 
        new_password=password_update.new_password,
        current_password=password_update.current_password
    )

@router.post("/update-username", response_model=AccountOut)
def update_username_endpoint(
    username_update: UsernameUpdateRequest,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Update username for current user
    """
    return update_username(
        db=db, 
        account=current_account, 
        new_username=username_update.new_username
    )

@router.put("/ban/{account_id}", response_model=AccountOut)
def ban_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """
    Admin ban a user (set status to banned)
    """
    db_account = account_service.ban_account(db=db, account_id=account_id)
    return db_account



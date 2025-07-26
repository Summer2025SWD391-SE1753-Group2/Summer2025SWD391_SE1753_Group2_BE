from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.account import AccountOut, AccountUpdate, AccountCreate, RoleNameEnum, PasswordUpdateRequest, UsernameUpdateRequest
from app.services.account_service import search_accounts_by_name, confirm_email, update_account_profile, update_account, delete_account, send_confirmation_email, get_account_profile, get_account, update_password, update_username, is_google_user
from app.core.deps import get_db, get_current_active_account
from app.db.models.account import Account, AccountStatusEnum
from app.services import account_service
from app.apis.v1.endpoints.check_role import check_roles
from fastapi.responses import RedirectResponse
from app.core import settings
from jose import jwt, JWTError
from app.core.settings import settings
from datetime import datetime, timezone

router = APIRouter()

DEFAULT_FE_URL = 'http://localhost:5173'

def get_db_simple():
    """Simple DB dependency without authentication middleware"""
    from app.db.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== PUBLIC ENDPOINTS (NO AUTHENTICATION) =====

@router.get("/test")
def test_endpoint():
    """Simple test endpoint"""
    return {"message": "Accounts router is working!", "timestamp": datetime.now().isoformat()}

@router.get("/reset-password")
def check_reset_token(token: str = Query(...)):
    """
    Check reset password token and redirect to frontend
    PUBLIC ENDPOINT - No authentication required
    """
    from app.db.database import SessionLocal
    
    frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FE_URL)
    db = SessionLocal()
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Check token type
        if payload.get("token_type") != "reset_password":
            redirect_url = f"{frontend_url}/reset-password?status=fail&error=invalid_token_type"
            return RedirectResponse(url=redirect_url)
        
        # Get username
        username = payload.get("sub")
        if not username:
            redirect_url = f"{frontend_url}/reset-password?status=fail&error=no_username"
            return RedirectResponse(url=redirect_url)
        
        # Check account exists
        account = db.query(Account).filter(Account.username == username).first()
        if not account:
            redirect_url = f"{frontend_url}/reset-password?status=fail&error=account_not_found"
            return RedirectResponse(url=redirect_url)
        
        # Check token in database
        from app.db.models.token import Token
        token_record = db.query(Token).filter(
            Token.access_token == token,
            Token.is_active == True,
            Token.token_type == "reset_password"
        ).first()
        
        if not token_record:
            redirect_url = f"{frontend_url}/reset-password?status=fail&error=token_not_found"
            return RedirectResponse(url=redirect_url)
        
        # Check token expiry
        if token_record.expires_at and token_record.expires_at < datetime.now(timezone.utc):
            token_record.is_active = False
            db.commit()
            redirect_url = f"{frontend_url}/reset-password?status=fail&error=token_expired"
            return RedirectResponse(url=redirect_url)
        
        # Token is valid
        redirect_url = f"{frontend_url}/reset-password?status=success&token={token}"
        return RedirectResponse(url=redirect_url)
        
    except JWTError:
        redirect_url = f"{frontend_url}/reset-password?status=fail&error=invalid_jwt"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        redirect_url = f"{frontend_url}/reset-password?status=fail&error=server_error"
        return RedirectResponse(url=redirect_url)
    finally:
        db.close()

@router.post("/reset-password")
def submit_reset_password(token: str, new_password: str, confirm_password: str):
    """
    Submit password reset
    PUBLIC ENDPOINT - No authentication required
    """
    from app.db.database import SessionLocal
    from app.core.security import get_password_hash
    
    if new_password != confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )
    
    db = SessionLocal()
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # Check token type
        if payload.get("token_type") != "reset_password":
            raise HTTPException(
                status_code=400,
                detail="Invalid token type"
            )
        
        # Get username
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=400,
                detail="Invalid token: missing username"
            )
        
        # Find account
        account = db.query(Account).filter(Account.username == username).first()
        if not account:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )
        
        # Check token in database
        from app.db.models.token import Token
        token_record = db.query(Token).filter(
            Token.access_token == token,
            Token.is_active == True,
            Token.token_type == "reset_password",
            Token.account_id == account.account_id
        ).first()
        
        if not token_record:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired token"
            )
        
        # Check token expiry
        if token_record.expires_at and token_record.expires_at < datetime.now(timezone.utc):
            token_record.is_active = False
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="Token has expired"
            )
        
        # Update password
        account.password_hash = get_password_hash(new_password)
        
        # Deactivate reset token
        token_record.is_active = False
        
        # Optional: Logout from all devices
        db.query(Token).filter(
            Token.account_id == account.account_id,
            Token.is_active == True,
            Token.token_type.in_(["access", "refresh"])
        ).update({"is_active": False})
        
        db.commit()
        
        return {
            "message": "Password reset successfully",
            "username": account.username
        }
        
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        db.close()

@router.get("/confirm-email")
async def confirm_email_get(token: str = Query(...), db: Session = Depends(get_db_simple)):
    """
    Confirm email with token (GET method)
    PUBLIC ENDPOINT - No authentication required
    """
    try:
        await confirm_email(db, token)
        frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FE_URL)
        redirect_url = f"{frontend_url}/verify-success?status=success"
        return RedirectResponse(url=redirect_url)
    except HTTPException as e:
        frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FE_URL)
        redirect_url = f"{frontend_url}/verify-success?status=fail"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        frontend_url = getattr(settings, 'FRONTEND_URL', DEFAULT_FE_URL)
        redirect_url = f"{frontend_url}/verify-success?status=fail"
        return RedirectResponse(url=redirect_url)

@router.post("/confirm-email")
async def confirm_email_post(token: str = Query(...), db: Session = Depends(get_db_simple)):
    """
    Confirm email with token (POST method)
    PUBLIC ENDPOINT - No authentication required
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

@router.post("/resend-confirmation")
async def resend_confirmation_email(username: str, db: Session = Depends(get_db_simple)):
    """
    Resend confirmation email
    PUBLIC ENDPOINT - No authentication required
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
async def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db_simple)
):
    """
    Create a new user account
    PUBLIC ENDPOINT - No authentication required
    """
    return await account_service.create_account(db=db, account=account)

# ===== DEBUG ENDPOINTS =====

@router.get("/debug-user/{username}")
def debug_user(username: str):
    """Debug endpoint to check user data"""
    from app.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        account = db.query(Account).filter(Account.username == username).first()
        
        if not account:
            return {"error": f"User {username} not found"}
        
        from app.db.models.token import Token
        tokens = db.query(Token).filter(Token.account_id == account.account_id).all()
        
        return {
            "username": account.username,
            "email": account.email,
            "status": account.status.value,
            "account_id": str(account.account_id),
            "tokens_count": len(tokens),
            "tokens": [
                {
                    "type": t.token_type,
                    "active": t.is_active,
                    "expires": str(t.expires_at),
                    "created": str(t.created_at)
                } for t in tokens
            ]
        }
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()

@router.get("/debug-jwt")
def debug_jwt(token: str = Query(...)):
    """Debug endpoint to decode JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return {"payload": payload}
    except Exception as e:
        return {"error": str(e)}

# ===== AUTHENTICATED ENDPOINTS =====

@router.get("/me", response_model=AccountOut)
def read_account_me(
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Get current account information"""
    return current_account

@router.get("/is-google-user")
def check_google_user(
    current_account: Account = Depends(get_current_active_account)
):
    """Check if current user is a Google user"""
    return {
        "is_google_user": is_google_user(current_account),
        "username": current_account.username,
        "email": current_account.email
    }

@router.put("/me", response_model=AccountOut)
async def update_account_me(
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Update current account information"""
    return await account_service.update_account_profile(
        db=db,
        account=current_account,
        profile_update=account_update
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

@router.get("/search/", response_model=List[AccountOut])
def search_accounts_endpoint(
    name: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Account = Depends(get_current_active_account)
):
    """Search accounts by username or full name"""
    return search_accounts_by_name(db, name, skip=skip, limit=limit)

@router.post("/moderator", response_model=AccountOut)
async def create_moderator(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Create a new moderator account - Only admin can create moderator accounts"""
    account.role_name = RoleNameEnum.moderator
    return await account_service.create_account(db=db, account=account)

@router.post("/update-password", response_model=AccountOut)
def update_password_endpoint(
    password_update: PasswordUpdateRequest,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.user, RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """Update password for current user"""
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
    """Update username for current user"""
    return update_username(
        db=db,
        account=current_account,
        new_username=username_update.new_username
    )

@router.get("/profiles/{username}", response_model=AccountOut)
async def view_profile(
    username: str,
    db: Session = Depends(get_db),
    current_account: Account = Depends(get_current_active_account)
):
    """View profile of a specific account"""
    return await get_account_profile(db, username)

@router.put("/ban/{account_id}", response_model=AccountOut)
def ban_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Admin ban a user (set status to banned)"""
    db_account = account_service.ban_account(db=db, account_id=account_id)
    return db_account

@router.put("/{account_id}", response_model=AccountOut)
async def update_account(
    account_id: str,
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.admin]))
):
    """Update account information - Only admin can update other accounts"""
    return await account_service.update_account(
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
    """Delete account - Only admin can delete accounts"""
    account_service.delete_account(db=db, account_id=account_id)

# ===== GENERIC ROUTES (MUST BE LAST) =====

@router.get("/{account_id}", response_model=AccountOut)
def read_account(
    account_id: str,
    db: Session = Depends(get_db),
    current_account: Account = Depends(check_roles([RoleNameEnum.moderator, RoleNameEnum.admin]))
):
    """
    Get account by ID - Only moderator and admin can view other accounts
    THIS ROUTE MUST BE LAST to avoid conflicts with specific routes
    """
    db_account = account_service.get_account(db=db, account_id=account_id)
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return db_account
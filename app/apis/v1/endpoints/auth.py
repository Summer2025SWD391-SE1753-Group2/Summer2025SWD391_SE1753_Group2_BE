from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Security, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, SecurityScopes
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.settings import settings
from app.schemas.token import Token, TokenData
from app.services.token_service import TokenService
from app.core.deps import get_db
from app.db.models.account import Account, AccountStatusEnum
from app.services.email_service import send_reset_password_email
from app.services.otp_service import send_otp, verify_otp
from app.schemas.account import AccountCreate, AccountOut, SendOTPRequest, VerifyPhoneRequest, VerifyPhoneResponse
from app.services.account_service import create_account
from app.services.google_auth_service import get_google_token, get_google_user_info, get_or_create_google_account

router = APIRouter()

JWT_SECRET_KEY=settings.JWT_SECRET_KEY
JWT_ALGORITHM=settings.JWT_ALGORITHM

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Update OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/access-token",
    scopes={
        "me": "Read information about the current user.",
        "items": "Read items."
    }
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)
def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)

def authenticate_account(db: Session, username_or_email: str, password: str):
    # Try to find account by username or email
    account = db.query(Account).filter(
        (Account.username == username_or_email) | (Account.email == username_or_email)
    ).first()
    
    if not account:
        return None, "Incorrect username/email or password"
    if not verify_password(password, account.password_hash):
        return None, "Incorrect username/email or password"
    if account.status != AccountStatusEnum.active:
        return None, "Account is not active. Please confirm your email first."
    return account, None

def create_access_token(user: Account) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    
    to_encode = {
        "sub": user.username,
        "user_id": str(user.account_id),
        "role": user.role.role_name,  # Add role to token
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> TokenData:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # Verify token in database
        token_record = TokenService.get_active_token(db, token)
        if not token_record:
            raise credentials_exception

        # Verify JWT token
        payload = TokenService.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user = db.query(Account).filter(Account.username == username).first()
        if user is None or user.status != AccountStatusEnum.active:
            raise credentials_exception
        
        token_data = TokenData(
            username=username,
            user_id=str(user.account_id),
            exp=payload.get("exp")
        )
        
        for scope in security_scopes.scopes:
            if scope not in payload.get("scopes", []):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        
        return token_data
    except JWTError:
        raise credentials_exception

@router.post("/access-token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user, error_message = authenticate_account(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create direct access token with role
    access_token = create_access_token(user)
    
    # Create refresh token with role
    token_data = {
        "sub": user.username,
        "user_id": str(user.account_id),
        "role": user.role.role_name,
        "scopes": form_data.scopes
    }
    refresh_token = TokenService.create_refresh_token(token_data)
    
    # Create token record
    token_record = TokenService.create_token_record(db, user, access_token, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh-token")
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    try:
        payload = TokenService.verify_token(refresh_token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data"
            )
        
        user = db.query(Account).filter(Account.username == username).first()
        if user is None or user.status != AccountStatusEnum.active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        token_data = {
            "sub": user.username,
            "user_id": str(user.account_id),
            "scopes": payload.get("scopes", [])
        }
        new_access_token = TokenService.create_access_token(token_data)
        
        # Create new token record
        token_record = TokenService.create_token_record(db, user, new_access_token)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

class ForgotPasswordRequest(BaseModel):
    username: str

class ForgotPasswordResponse(BaseModel):
    message: str
    method: str
    username: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class ResetPasswordResponse(BaseModel):
    message: str
    username: str

class ResetPasswordOTPRequest(BaseModel):
    username: str
    otp: str
    new_password: str
    confirm_password: str

class ResetPasswordOTPResponse(BaseModel):
    message: str
    username: str

@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    # Find account
    account = db.query(Account).filter(Account.username == request.username).first()
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    
    if account.status != AccountStatusEnum.active:
        raise HTTPException(
            status_code=400,
            detail="Account is not active"
        )

    # If account has phone number, send OTP
    if account.phone_number and account.phone_verified:
        otp = await send_otp(account.phone_number)
        return {
            "message": "OTP sent to your phone number",
            "method": "phone",
            "username": account.username
        }
    
    # Otherwise, send reset password email
    await send_reset_password_email(account.email, account.username)
    return {
        "message": "Reset password instructions sent to your email",
        "method": "email",
        "username": account.username
    }

@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    # Check if passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    try:
        # Verify token
        payload = jwt.decode(request.token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
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
        
        # Update password
        account.password_hash = get_password_hash(request.new_password)
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

@router.post("/reset-password-otp", response_model=ResetPasswordOTPResponse)
async def reset_password_otp(
    request: ResetPasswordOTPRequest,
    db: Session = Depends(get_db)
):
    # Check if passwords match
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    # Find account
    account = db.query(Account).filter(Account.username == request.username).first()
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    
    if not account.phone_number or not account.phone_verified:
        raise HTTPException(
            status_code=400,
            detail="Phone number not verified"
        )
    
    # Verify OTP
    if not await verify_otp(account.phone_number, request.otp):
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )
    
    # Update password
    account.password_hash = get_password_hash(request.new_password)
    db.commit()
    
    return {
        "message": "Password reset successfully",
        "username": account.username
    }

@router.post("/send-otp")
async def send_otp_phone(
    data: SendOTPRequest,
    db: Session = Depends(get_db),
    token_data: TokenData = Depends(get_current_user)
):
    """
    Gửi OTP xác thực số điện thoại để nâng cấp user lên user_l2.
    - Chỉ cho phép nếu user chưa có phone_number hoặc phone_verified=False.
    - phone_number là unique.
    - OTP có hiệu lực 5 phút.
    """
    phone_number = data.phone_number
    user = db.query(Account).filter(Account.username == token_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    if user.phone_verified:
        raise HTTPException(status_code=400, detail="Phone number already verified")
    existing = db.query(Account).filter(Account.phone_number == phone_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already in use")
    await send_otp(phone_number)
    user.phone_number = phone_number
    user.phone_verified = False
    db.commit()
    return {"message": f"OTP sent to {phone_number}. OTP is valid for 5 minutes."}

@router.post("/verify-phone", response_model=VerifyPhoneResponse)
async def verify_phone(
    request: VerifyPhoneRequest,
    db: Session = Depends(get_db),
    token_data: TokenData = Depends(get_current_user)
):
    """
    Xác thực OTP cho số điện thoại để nâng cấp user lên user_l2.
    - Nếu OTP đúng và còn hạn: phone_verified=True, role_id=2 (user_l2)
    - Nếu OTP sai/hết hạn: báo lỗi
    """
    user = db.query(Account).filter(Account.username == token_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found")
    if not user.phone_number or user.phone_number != request.phone_number:
        raise HTTPException(status_code=400, detail="Phone number mismatch")
    if user.phone_verified:
        raise HTTPException(status_code=400, detail="Phone number already verified")
    if not await verify_otp(user.phone_number, request.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    user.phone_verified = True
    user.role_id = 2  # user_l2
    db.commit()
    return {
        "message": "Phone number verified successfully. Account upgraded to Level 2.",
        "username": user.username,
        "role": "user_l2"
    }

class VerifyEmailRequest(BaseModel):
    username: str
    token: str

class VerifyEmailResponse(BaseModel):
    message: str
    username: str
    email: str

@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    try:
        # Verify token
        payload = jwt.decode(request.token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        new_email: str = payload.get("email")
        
        if username is None or new_email is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid token"
            )
        
        if username != request.username:
            raise HTTPException(
                status_code=400,
                detail="Token username mismatch"
            )
        
        # Get account
        account = db.query(Account).filter(Account.username == username).first()
        if account is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )
        
        # Check if new email is already in use
        existing_email = db.query(Account).filter(
            Account.email == new_email,
            Account.account_id != account.account_id
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already in use"
            )
        
        # Update email and set email_verified to True
        account.email = new_email
        account.email_verified = True
        db.commit()
        db.refresh(account)
        
        return {
            "message": "Email verified and updated successfully",
            "username": account.username,
            "email": account.email
        }
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token"
        )

@router.post("/register", response_model=AccountOut)
async def register(account: AccountCreate, db: Session = Depends(get_db)):
    """
    Register a new account
    """
    return await create_account(db, account)

@router.post("/access-token")
async def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    account, error_message = authenticate_account(db, form_data.username, form_data.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(account.username),
        "token_type": "bearer"
    }

@router.get("/google/login")
async def google_login():
    """
    Redirect to Google OAuth login page
    """
    return {
        "url": f"https://accounts.google.com/o/oauth2/v2/auth?"
               f"client_id={settings.CLIENT_ID}&"
               f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
               f"response_type=code&"
               f"scope=email profile&"
               f"access_type=offline&"
               f"prompt=consent"
    }

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback
    """
    # Get Google token
    google_token = await get_google_token(code)
    
    # Get Google user info
    google_user = await get_google_user_info(google_token.access_token)
    
    # Get or create account
    account = await get_or_create_google_account(db, google_user)
    
    # Create access token
    token_data = {
        "sub": account.username,
        "user_id": str(account.account_id),
        "scopes": ["me"]
    }
    
    access_token = TokenService.create_access_token(token_data)
    refresh_token = TokenService.create_refresh_token(token_data)
    
    # Create token record
    token_record = TokenService.create_token_record(db, account, access_token, refresh_token)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Logout by deactivating the current access token
    """
    # Get the token record
    token_record = TokenService.get_active_token(db, token)
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Deactivate the token
    TokenService.deactivate_token(db, token_record.token_id)
    
    return {
        "message": "Successfully logged out"
    }

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
from app.schemas.account import AccountCreate, AccountOut
from app.services.account_service import create_account

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

def authenticate_account(db: Session, username: str, password: str):
    user = db.query(Account).filter(Account.username == username).first()
    if not user:
        return None, "Incorrect username or password"
    if not verify_password(password, user.password_hash):
        return None, "Incorrect username or password"
    if user.status != AccountStatusEnum.active:
        return None, "Account is not active. Please confirm your email first."
    return user, None

def create_access_token(username: str) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": username,
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
    
    token_data = {
        "sub": user.username,
        "user_id": str(user.account_id),
        "scopes": form_data.scopes
    }
    
    access_token = TokenService.create_access_token(token_data)
    refresh_token = TokenService.create_refresh_token(token_data)
    
    # Create token record in database
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

class VerifyPhoneRequest(BaseModel):
    username: str
    otp: str

class VerifyPhoneResponse(BaseModel):
    message: str
    username: str
    role: str

@router.post("/verify-phone", response_model=VerifyPhoneResponse)
async def verify_phone(
    request: VerifyPhoneRequest,
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
    
    if not account.phone_number:
        raise HTTPException(
            status_code=400,
            detail="No phone number registered"
        )
    
    if account.phone_verified:
        raise HTTPException(
            status_code=400,
            detail="Phone number already verified"
        )
    
    # Verify OTP
    if not await verify_otp(account.phone_number, request.otp):
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )
    
    # Update account
    account.phone_verified = True
    account.role_id = 2  # Upgrade to user_l2
    db.commit()
    
    return {
        "message": "Phone number verified successfully. Account upgraded to Level 2.",
        "username": account.username,
        "role": "user l2"
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

from datetime import timedelta, datetime, timezone
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Security, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, SecurityScopes
from fastapi.responses import RedirectResponse
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
from app.services.account_service import create_account as service_create_account
from app.services.google_auth_service import get_google_token, get_google_user_info, get_or_create_google_account

router = APIRouter()

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

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

def create_access_token(user: Account, scopes: Optional[list] = None) -> str:
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode = {
        "sub": user.username,
        "user_id": str(user.account_id),
        "role": user.role.role_name,
        "exp": expire,
        "scopes": scopes if scopes is not None else []
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
        token_record = TokenService.get_active_token(db, token)
        if not token_record:
            raise credentials_exception

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

    access_token = create_access_token(user, scopes=form_data.scopes)

    refresh_token_payload = {
        "sub": user.username,
        "user_id": str(user.account_id),
        "role": user.role.role_name,
        "scopes": form_data.scopes
    }
    refresh_token = TokenService.create_refresh_token(refresh_token_payload)

    TokenService.create_token_record(db, user, access_token, refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    refresh_token_str: Annotated[str, Body(embed=True, alias="refresh_token")],
    db: Session = Depends(get_db)
):
    try:
        payload = TokenService.verify_token(refresh_token_str)
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

        new_access_token_payload = {
            "sub": user.username,
            "user_id": str(user.account_id),
            "role": user.role.role_name,
            "scopes": payload.get("scopes", [])
        }
        new_access_token = create_access_token(user, scopes=new_access_token_payload["scopes"])

        TokenService.create_token_record(db, user, new_access_token)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token_str
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
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

    if account.phone_number and account.phone_verified:
        await send_otp(account.phone_number)
        return {
            "message": "OTP sent to your phone number",
            "method": "phone",
            "username": account.username
        }

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
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    try:
        payload = jwt.decode(request.token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid token"
            )

        account = db.query(Account).filter(Account.username == username).first()
        if account is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

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
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match"
        )

    account = db.query(Account).filter(Account.username == request.username).first()
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if not account.phone_number or not account.phone_verified:
        raise HTTPException(
            status_code=400,
            detail="Phone number not verified or not registered for this account."
        )

    if not await verify_otp(account.phone_number, request.otp):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

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
    # FIX: Remove Depends() around Security()
    token_data: TokenData = Security(get_current_user, scopes=["me"])
):
    phone_number = data.phone_number
    user = db.query(Account).filter(Account.account_id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Authenticated account not found.")

    if user.phone_verified:
        raise HTTPException(status_code=400, detail="Phone number is already verified for this account.")

    existing_phone_user = db.query(Account).filter(
        Account.phone_number == phone_number,
        Account.account_id != user.account_id
    ).first()
    if existing_phone_user:
        raise HTTPException(status_code=400, detail="This phone number is already in use by another account.")

    await send_otp(phone_number)

    user.phone_number = phone_number
    user.phone_verified = False
    db.commit()
    db.refresh(user)

    return {"message": f"OTP sent to {phone_number}. OTP is valid for 5 minutes."}

@router.post("/verify-phone", response_model=VerifyPhoneResponse)
async def verify_phone(
    request: VerifyPhoneRequest,
    db: Session = Depends(get_db),
    # FIX: Remove Depends() around Security()
    token_data: TokenData = Security(get_current_user, scopes=["me"])
):
    user = db.query(Account).filter(Account.account_id == token_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Authenticated account not found.")

    if not user.phone_number or user.phone_number != request.phone_number:
        raise HTTPException(status_code=400, detail="Phone number mismatch or not registered for this account.")

    if user.phone_verified:
        raise HTTPException(status_code=400, detail="Phone number is already verified.")

    if not await verify_otp(user.phone_number, request.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    user.phone_verified = True
    db.commit()
    db.refresh(user)

    return {
        "message": "Phone number verified successfully.",
        "username": user.username,
        "role": user.role.role_name if user.role else "user"
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
        payload = jwt.decode(request.token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username_from_token: str = payload.get("sub")
        new_email_from_token: str = payload.get("email")

        if username_from_token is None or new_email_from_token is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid token data. Token is missing username or email."
            )

        if username_from_token != request.username:
            raise HTTPException(
                status_code=400,
                detail="Username in token does not match provided username."
            )

        account = db.query(Account).filter(Account.username == username_from_token).first()
        if account is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found."
            )

        existing_email_account = db.query(Account).filter(
            Account.email == new_email_from_token,
            Account.account_id != account.account_id
        ).first()
        if existing_email_account:
            raise HTTPException(
                status_code=400,
                detail="This email address is already in use by another account."
            )

        account.email = new_email_from_token
        account.email_verified = True
        db.commit()
        db.refresh(account)

        return {
            "message": "Email verified and updated successfully.",
            "username": account.username,
            "email": account.email
        }
    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired token."
        )

@router.post("/register", response_model=AccountOut)
async def register(account: AccountCreate, db: Session = Depends(get_db)):
    return await service_create_account(db, account)

@router.get("/google/login")
async def google_login():
    return RedirectResponse(
        url=f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.CLIENT_ID}&"
            f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
            f"response_type=code&"
            f"scope=email profile&"
            f"access_type=offline&"
            f"prompt=consent"
    )

@router.post("/google/callback")
async def google_callback_exchange(
    request_body: Annotated[dict, Body(embed=False)],
    db: Session = Depends(get_db)
):
    code = request_body.get("code")
    if not code:
        raise HTTPException(
            status_code=400,
            detail="Authorization code is required in the request body."
        )
    try:
        google_token = await get_google_token(code)
        google_user = await get_google_user_info(google_token.access_token)
        account = await get_or_create_google_account(db, google_user)

        access_token_payload = {
            "sub": account.username,
            "user_id": str(account.account_id),
            "role": account.role.role_name if account.role else "user",
            "scopes": ["me"]
        }
        access_token = create_access_token(account, scopes=access_token_payload["scopes"])

        refresh_token_payload = {
            "sub": account.username,
            "user_id": str(account.account_id),
            "role": account.role.role_name if account.role else "user",
            "scopes": ["me"]
        }
        refresh_token = TokenService.create_refresh_token(refresh_token_payload)

        TokenService.create_token_record(db, account, access_token, refresh_token)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "account_id": account.account_id,
                "username": account.username,
                "email": account.email,
                "full_name": account.full_name,
                "role": account.role.role_name if account.role else "user",
                "phone_verified": account.phone_verified,
                "email_verified": account.email_verified,
                "status": account.status.value
            }
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Google OAuth exchange error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange authorization code: {str(e)}"
        )

@router.get("/google/callback")
async def google_callback_redirect_to_frontend(
    code: Optional[str] = None,
    error: Optional[str] = None,
    state: Optional[str] = None
):
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')

    redirect_params = []
    if code:
        redirect_params.append(f"code={code}")
    if error:
        redirect_params.append(f"error={error}")
    if state:
        redirect_params.append(f"state={state}")

    redirect_url = f"{frontend_url}/auth/google/callback"
    if redirect_params:
        redirect_url += "?" + "&".join(redirect_params)

    return RedirectResponse(url=redirect_url)


@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    token_record = TokenService.get_active_token(db, token)
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or already logged out token."
        )

    TokenService.deactivate_token(db, token_record.token_id)

    return {
        "message": "Successfully logged out."
    }
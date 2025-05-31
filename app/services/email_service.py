from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.settings import settings
from pathlib import Path
import jwt
from datetime import datetime, timedelta, timezone
from jinja2 import Environment, FileSystemLoader
import os

# Configure Jinja2
template_dir = Path(__file__).parent.parent / 'templates'
env = Environment(loader=FileSystemLoader(template_dir))

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_confirmation_email(email: str, username: str):
    # Create confirmation token
    token_data = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    # Create confirmation link - using the API endpoint directly
    # BE if FE is not existed
    base_url = settings.BACKEND_CORS_ORIGINS[0] if isinstance(settings.BACKEND_CORS_ORIGINS, list) else settings.BACKEND_CORS_ORIGINS
    # Remove trailing slash from base_url if exists
    base_url = base_url.rstrip('/')
    # Remove leading slash from API_V1_STR if exists
    api_path = settings.API_V1_STR.lstrip('/')
    confirmation_link = f"{base_url}/{api_path}/accounts/confirm-email?token={token}"
    
    # Load and render template
    template = env.get_template('email_confirmation.html')
    html_content = template.render(
        project_name=settings.PROJECT_NAME,
        username=username,
        confirmation_link=confirmation_link,
        expire_hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS
    )
    
    # Create email message
    message = MessageSchema(
        subject=f"Welcome to {settings.PROJECT_NAME} - Confirm Your Email",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    
    # Send email
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_reset_password_email(email: str, username: str):
    # Create reset password token
    token_data = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    # Create reset password link
    base_url = settings.BACKEND_CORS_ORIGINS[0] if isinstance(settings.BACKEND_CORS_ORIGINS, list) else settings.BACKEND_CORS_ORIGINS
    base_url = base_url.rstrip('/')
    api_path = settings.API_V1_STR.lstrip('/')
    reset_link = f"{base_url}/{api_path}/auth/reset-password?token={token}"
    
    # Load and render template
    template = env.get_template('reset_password.html')
    html_content = template.render(
        project_name=settings.PROJECT_NAME,
        username=username,
        reset_link=reset_link,
        expire_hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS
    )
    
    # Create email message
    message = MessageSchema(
        subject=f"{settings.PROJECT_NAME} - Reset Your Password",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    
    # Send email
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_email_verification(email: str, username: str, new_email: str):
    token_data = {
        "sub": username,
        "email": new_email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    subject = "Verify your new email address"
    body = f"""
    Hello {username},
    
    You have requested to change your email address to {new_email}.
    Please click the link below to verify your new email address:
    
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you did not request this change, please ignore this email.
    
    Best regards,
    Your App Team
    """
    
    await send_email(email, subject, body) 
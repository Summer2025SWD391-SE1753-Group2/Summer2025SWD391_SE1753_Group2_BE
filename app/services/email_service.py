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
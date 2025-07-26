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
    """
    Send confirmation email to newly registered user.
    Raises exception if email sending fails.
    """
    # Validate inputs before processing
    if not email or not email.strip():
        raise ValueError("Email address is required and cannot be empty")
    
    if not username or not username.strip():
        raise ValueError("Username is required and cannot be empty")
    
    # Basic email format validation
    if "@" not in email or "." not in email:
        raise ValueError("Invalid email format")
    
    try:
        # Create confirmation token
        token_data = {
            "sub": username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
        }
        token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        
        # Create confirmation link - BE xác thực, FE sẽ nhận redirect về login
        confirmation_link = f"{settings.BACKEND_URL}{settings.API_V1_STR}/accounts/confirm-email?token={token}"
        
        # Validate template exists before rendering
        try:
            template = env.get_template('email_confirmation.html')
        except Exception as template_error:
            raise Exception(f"Email template not found: {str(template_error)}")
        
        # Render template
        html_content = template.render(
            project_name=settings.PROJECT_NAME,
            name=username,
            verification_link=confirmation_link,
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
        
        print(f"Confirmation email sent successfully to {email} for user {username}")
        
    except ValueError:
        # Re-raise validation errors
        raise
    except Exception as e:
        print(f"Failed to send confirmation email to {email} for user {username}: {str(e)}")
        raise Exception(f"Email sending failed: {str(e)}")

async def send_email_verification(email: str, username: str, new_email: str):
    token_data = {
        "sub": username,
        "email": new_email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24)
    }
    token = jwt.encode(token_data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    verification_url = f"https://swd.nhducminhqt.name.vn/verify-email?token={token}"
    
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
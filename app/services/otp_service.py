import random
import string
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from app.core.settings import settings

# In-memory storage for OTPs (in production, use Redis or similar)
otp_store: Dict[str, Dict[str, any]] = {}

async def send_otp(phone_number: str) -> str:
    """
    Generate and send OTP to phone number.
    In production, integrate with SMS service provider.
    """
    # Generate 6-digit OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    # Store OTP with expiration
    otp_store[phone_number] = {
        'otp': otp,
        'expires_at': datetime.now(timezone.utc) + timedelta(minutes=5)
    }
    
    # In production, send SMS here
    # For development, just print the OTP
    print(f"OTP for {phone_number}: {otp}")
    
    return otp

async def verify_otp(phone_number: str, otp: str) -> bool:
    """
    Verify OTP for phone number.
    """
    stored_data = otp_store.get(phone_number)
    if not stored_data:
        return False
    
    # Check if OTP is expired
    if datetime.now(timezone.utc) > stored_data['expires_at']:
        del otp_store[phone_number]
        return False
    
    # Check if OTP matches
    if stored_data['otp'] != otp:
        return False
    
    # Remove OTP after successful verification
    del otp_store[phone_number]
    return True 
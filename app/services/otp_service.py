import random
import time
from fastapi import HTTPException
from twilio.rest import Client
from app.core.settings import settings

# In-memory OTP store (có thể thay bằng Redis cho production)
otp_storage = {}

twilio_client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)

def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices('0123456789', k=length))

def send_otp_sms(phone_number: str, otp: str):
    try:
        message = twilio_client.messages.create(
            body=f"Your OTP code is: {otp}",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        print(f"OTP sent to {phone_number}: {message.sid}")
    except Exception as e:
        print(f"Failed to send OTP: {e}")
        raise HTTPException(status_code=500, detail="Failed to send OTP")

async def send_otp(phone_number: str) -> str:
    otp = generate_otp()
    otp_storage[phone_number] = {
        "otp": otp,
        "timestamp": time.time()
    }
    send_otp_sms(phone_number, otp)
    return otp

async def verify_otp(phone_number: str, otp: str) -> bool:
    if phone_number not in otp_storage:
        return False
    stored_otp = otp_storage[phone_number]["otp"]
    timestamp = otp_storage[phone_number]["timestamp"]
    if time.time() - timestamp > 300:  # 5 phút
        del otp_storage[phone_number]
        return False
    if stored_otp != otp:
        return False
    del otp_storage[phone_number]
    return True 
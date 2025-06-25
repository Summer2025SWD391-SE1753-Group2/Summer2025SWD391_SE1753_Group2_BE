#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("=== Environment Variables Test ===")
print(f"GOOGLE_REDIRECT_URI: {os.getenv('GOOGLE_REDIRECT_URI', 'Not found')}")
print(f"FRONTEND_URL: {os.getenv('FRONTEND_URL', 'Not found')}")

try:
    from app.core.settings import settings
    print("\n=== Settings Test ===")
    print(f"settings.GOOGLE_REDIRECT_URI: {settings.GOOGLE_REDIRECT_URI}")
    print(f"settings.FRONTEND_URL: {settings.FRONTEND_URL}")
except Exception as e:
    print(f"\nError loading settings: {e}") 
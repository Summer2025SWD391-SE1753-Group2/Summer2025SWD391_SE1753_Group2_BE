import re
from fastapi import HTTPException
from email_validator import validate_email, EmailNotValidError
from datetime import datetime, date
from typing import Union

def validate_username(username: str):
    if not re.match(r"^\w+$", username):
        raise HTTPException(
            status_code=400,
            detail="Username must contain only letters, numbers, and underscores (_)."
        )
    if not (3 <= len(username) <= 30):
        raise HTTPException(
            status_code=400,
            detail="Username must be between 3 and 30 characters."
        )
    return username


def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters."
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one uppercase letter."
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one lowercase letter."
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Password must include at least one digit."
        )
    return password


def validate_email_address(email: str):
    try:
        # normalize & validate
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))


def validate_phone_number(phone: str):
    if not re.fullmatch(r"^0\d{9}$", phone):  # Vietnam 10 digits starting with 0
        raise HTTPException(
            status_code=400,
            detail="Phone number must be 10 digits and start with 0."
        )
    return phone


def validate_full_name(name: str):
    if not re.match(r"^[a-zA-ZÀ-ỹ\s'.-]+$", name):
        raise HTTPException(
            status_code=400,
            detail="Full name must contain only letters and spaces."
        )
    if len(name.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Full name is too short."
        )
    return name

def validate_date_of_birth(dob: Union[str, date]) -> date:
    try:
        if isinstance(dob, str):
            date_of_birth = datetime.strptime(dob, "%Y-%m-%d").date()
        elif isinstance(dob, date):
            date_of_birth = dob
        else:
            raise ValueError("Invalid date format")

        if date_of_birth >= datetime.now().date():
            raise HTTPException(
                status_code=400,
                detail="Date of birth must be in the past."
            )
        return date_of_birth
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail="Date of birth must be in the format YYYY-MM-DD."
        )
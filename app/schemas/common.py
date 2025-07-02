from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID

class AccountSummary(BaseModel):
    """Common schema for account summary information used across multiple endpoints"""
    account_id: UUID
    username: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True) 
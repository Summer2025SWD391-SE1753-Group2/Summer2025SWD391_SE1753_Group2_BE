from typing import List, Optional
from pydantic import BaseModel, UUID4
from datetime import datetime
from .post import PostOut

class FavouriteBase(BaseModel):
    favourite_name: str

class FavouriteCreate(FavouriteBase):
    pass

class FavouriteUpdate(FavouriteBase):
    pass

class FavouriteInDB(FavouriteBase):
    favourite_id: UUID4
    account_id: UUID4
    created_at: datetime

    class Config:
        from_attributes = True

class FavouriteCreateResponse(FavouriteInDB):
    """Response schema for creating a new favourite list"""
    pass

class FavouriteResponse(FavouriteInDB):
    """Response schema for getting a favourite list with its posts"""
    posts: List[PostOut] = []

class FavouriteListResponse(FavouriteInDB):
    """Response schema for listing favourite lists"""
    post_count: int = 0 